"""
FastAPI backend for Post Discharge Medical AI Assistant.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import uvicorn
from datetime import datetime

from .agents.agent_graph import create_multi_agent_system
from .database.database import get_db_manager
from .rag.vector_store_openai import get_vector_store  # Using OpenAI embeddings
from .utils.logger import system_logger
from .config import settings

# Initialize FastAPI app
app = FastAPI(
    title="Post Discharge Medical AI Assistant",
    description="Multi-agent AI system for post-discharge patient care",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global instances
multi_agent_system = None
db_manager = None
vector_store = None


# Pydantic models
class ChatMessage(BaseModel):
    """Chat message model."""
    message: str
    session_id: Optional[str] = None


class ChatResponse(BaseModel):
    """Chat response model."""
    response: str
    session_id: str
    agent: str
    timestamp: str


class PatientQuery(BaseModel):
    """Patient query model."""
    patient_name: str


class SystemStatus(BaseModel):
    """System status model."""
    status: str
    database_patients: int
    vector_store_documents: int
    environment: str


@app.on_event("startup")
async def startup_event():
    """Initialize system on startup."""
    global multi_agent_system, db_manager, vector_store
    
    try:
        system_logger.info("Starting Post Discharge Medical AI Assistant...")
        
        # Initialize database
        system_logger.info("Initializing database...")
        db_manager = get_db_manager()
        
        # Load patient data
        try:
            db_manager.load_patient_data("./data/patient_reports.json")
        except Exception as e:
            system_logger.warning(f"Could not load patient data: {e}")
        
        # Initialize vector store
        system_logger.info("Initializing vector store...")
        vector_store = get_vector_store()
        
        # Index nephrology reference if not already indexed
        try:
            stats = vector_store.get_collection_stats()
            if stats.get("count", 0) == 0:
                system_logger.info("Indexing nephrology reference materials...")
                
                # Try PDF first, then fallback to text file
                from pathlib import Path
                pdf_file = Path("./knowledge base for RAG/comprehensive-clinical-nephrology.pdf")
                txt_file = Path("./data/nephrology_reference.txt")
                
                if pdf_file.exists():
                    system_logger.info("Using PDF reference (comprehensive clinical nephrology)")
                    vector_store.index_document(
                        str(pdf_file),
                        metadata={"type": "reference", "subject": "nephrology", "format": "pdf"}
                    )
                elif txt_file.exists():
                    system_logger.info("Using text reference")
                    vector_store.index_document(
                        str(txt_file),
                        metadata={"type": "reference", "subject": "nephrology", "format": "txt"}
                    )
                else:
                    system_logger.warning("No reference materials found")
        except Exception as e:
            system_logger.warning(f"Could not index reference materials: {e}")
        
        # Initialize multi-agent system
        system_logger.info("Initializing multi-agent system...")
        multi_agent_system = create_multi_agent_system()
        
        system_logger.info("✅ System startup complete!")
        
    except Exception as e:
        system_logger.log_error("StartupError", f"Failed to start system: {str(e)}")
        raise


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Post Discharge Medical AI Assistant API",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


@app.get("/status", response_model=SystemStatus)
async def system_status():
    """Get system status."""
    try:
        # Get database stats
        patients = db_manager.get_all_patients()
        patient_count = len(patients)
        
        # Get vector store stats
        vs_stats = vector_store.get_collection_stats()
        doc_count = vs_stats.get("count", 0)
        
        return SystemStatus(
            status="operational",
            database_patients=patient_count,
            vector_store_documents=doc_count,
            environment=settings.environment
        )
    except Exception as e:
        system_logger.log_error("StatusError", str(e))
        raise HTTPException(status_code=500, detail="Error getting system status")


@app.post("/chat", response_model=ChatResponse)
async def chat(message: ChatMessage):
    """
    Process a chat message.
    
    Args:
        message: Chat message from user
        
    Returns:
        Chat response from agent
    """
    try:
        system_logger.info(f"Received chat message: {message.message[:50]}...")
        
        # Process message through multi-agent system
        response = multi_agent_system.process_message(message.message)
        
        # Get current agent
        current_agent = multi_agent_system.state.get("current_agent", "receptionist")
        
        return ChatResponse(
            response=response,
            session_id=multi_agent_system.session_id,
            agent=current_agent,
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        system_logger.log_error("ChatError", f"Error processing chat: {str(e)}")
        raise HTTPException(status_code=500, detail="Error processing message")


@app.post("/reset")
async def reset_session():
    """Reset the current session."""
    try:
        multi_agent_system.reset_session()
        return {
            "message": "Session reset successfully",
            "session_id": multi_agent_system.session_id
        }
    except Exception as e:
        system_logger.log_error("ResetError", str(e))
        raise HTTPException(status_code=500, detail="Error resetting session")


@app.get("/patients")
async def get_patients():
    """Get all patients."""
    try:
        patients = db_manager.get_all_patients()
        return {"patients": patients, "count": len(patients)}
    except Exception as e:
        system_logger.log_error("PatientsError", str(e))
        raise HTTPException(status_code=500, detail="Error retrieving patients")


@app.post("/patient")
async def get_patient(query: PatientQuery):
    """Get a specific patient by name."""
    try:
        patient = db_manager.get_patient_by_name(query.patient_name)
        if patient is None:
            raise HTTPException(status_code=404, detail="Patient not found")
        return {"patient": patient}
    except HTTPException:
        raise
    except Exception as e:
        system_logger.log_error("PatientError", str(e))
        raise HTTPException(status_code=500, detail="Error retrieving patient")


@app.get("/history")
async def get_conversation_history():
    """Get conversation history for current session."""
    try:
        history = multi_agent_system.get_conversation_history()
        formatted_history = []
        
        for msg in history:
            formatted_history.append({
                "role": "user" if msg.type == "human" else "assistant",
                "content": msg.content,
                "timestamp": datetime.now().isoformat()
            })
        
        return {
            "session_id": multi_agent_system.session_id,
            "history": formatted_history
        }
    except Exception as e:
        system_logger.log_error("HistoryError", str(e))
        raise HTTPException(status_code=500, detail="Error retrieving history")


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
