"""
Simplified FastAPI backend for Post Discharge Medical AI Assistant.
This version starts without requiring vector store initialization.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import os

# Set environment variable to skip vector store initialization
os.environ['SKIP_VECTOR_INIT'] = '1'

from .database.database import get_db_manager
from .utils.logger import system_logger

# Initialize FastAPI app
app = FastAPI(
    title="Post Discharge Medical AI Assistant",
    description="Multi-agent AI system for post-discharge patient care",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global instances
db_manager = None


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
    global db_manager
    
    try:
        system_logger.info("Starting Post Discharge Medical AI Assistant (Simplified Mode)...")
        
        # Initialize database
        system_logger.info("Initializing database...")
        db_manager = get_db_manager()
        
        # Load patient data
        try:
            db_manager.load_patient_data("./data/patient_reports.json")
        except Exception as e:
            system_logger.warning(f"Could not load patient data: {e}")
        
        system_logger.info("✅ System startup complete (Simplified Mode)!")
        system_logger.info("Note: Vector store and AI agents are disabled in this mode")
        
    except Exception as e:
        system_logger.log_error("StartupError", f"Failed to start system: {str(e)}")
        raise


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Post Discharge Medical AI Assistant API (Simplified Mode)",
        "version": "1.0.0",
        "status": "running",
        "note": "Vector store and AI agents disabled - database only"
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
        
        return SystemStatus(
            status="operational (simplified mode)",
            database_patients=patient_count,
            vector_store_documents=0,
            environment="development"
        )
    except Exception as e:
        system_logger.log_error("StatusError", str(e))
        raise HTTPException(status_code=500, detail="Error getting system status")


@app.post("/chat", response_model=ChatResponse)
async def chat(message: ChatMessage):
    """
    Process a chat message (simplified - returns demo response).
    """
    try:
        system_logger.info(f"Received chat message: {message.message[:50]}...")
        
        # Simple demo response
        response = f"🤖 Demo Mode: I received your message '{message.message}'. "
        response += "The full AI system with agents and RAG is initializing. "
        response += "For now, you can test the patient database using the /patient endpoint."
        
        return ChatResponse(
            response=response,
            session_id="demo-session",
            agent="demo",
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        system_logger.log_error("ChatError", f"Error processing chat: {str(e)}")
        raise HTTPException(status_code=500, detail="Error processing message")


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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
