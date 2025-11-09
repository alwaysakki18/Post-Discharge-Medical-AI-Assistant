"""
Demo FastAPI backend with simulated multi-agent workflow.
This version works WITHOUT requiring OpenAI API key.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import uuid

from .database.database import get_db_manager
from .utils.logger import system_logger
from .utils.pdf_generator import generate_patient_pdf

# Initialize FastAPI app
app = FastAPI(
    title="Post Discharge Medical AI Assistant (Demo Mode)",
    description="Multi-agent AI system demo with simulated responses",
    version="1.0.0-demo"
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
conversation_state = {}


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
        system_logger.info("Starting Post Discharge Medical AI Assistant (Demo Mode)...")
        
        # Initialize database
        system_logger.info("Initializing database...")
        db_manager = get_db_manager()
        
        # Load patient data
        try:
            db_manager.load_patient_data("./data/patient_reports.json")
        except Exception as e:
            system_logger.warning(f"Could not load patient data: {e}")
        
        system_logger.info("✅ System startup complete (Demo Mode)!")
        system_logger.info("Note: Using simulated AI responses - no API key required")
        
    except Exception as e:
        system_logger.log_error("StartupError", f"Failed to start system: {str(e)}")
        raise


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Post Discharge Medical AI Assistant API (Demo Mode)",
        "version": "1.0.0-demo",
        "status": "running",
        "note": "Simulated multi-agent responses - no API key required"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


@app.get("/status", response_model=SystemStatus)
async def system_status():
    """Get system status."""
    try:
        patients = db_manager.get_all_patients()
        patient_count = len(patients)
        
        return SystemStatus(
            status="operational (demo mode)",
            database_patients=patient_count,
            vector_store_documents=150,  # Simulated
            environment="demo"
        )
    except Exception as e:
        system_logger.log_error("StatusError", str(e))
        raise HTTPException(status_code=500, detail="Error getting system status")


@app.post("/chat", response_model=ChatResponse)
async def chat(message: ChatMessage):
    """
    Process a chat message with simulated multi-agent workflow.
    """
    try:
        # Create or get session
        session_id = message.session_id or str(uuid.uuid4())
        if session_id not in conversation_state:
            conversation_state[session_id] = {
                "stage": "greeting",
                "patient_name": None,
                "patient_data": None
            }
        
        state = conversation_state[session_id]
        user_message = message.message.lower().strip()
        
        system_logger.info(f"[Session {session_id[:8]}] User: {message.message}")
        
        # STAGE 1: Greeting (Receptionist Agent)
        if state["stage"] == "greeting":
            response = "👋 Hello! I'm your post-discharge care assistant. I'm here to help you with your recovery. What's your name?"
            agent = "Receptionist Agent"
            state["stage"] = "awaiting_name"
        
        # STAGE 2: Get patient name and retrieve data (Receptionist Agent)
        elif state["stage"] == "awaiting_name":
            # Extract potential name from message
            patient_name = message.message.strip()
            
            # Try to find patient in database
            patient = db_manager.get_patient_by_name(patient_name)
            
            if patient:
                state["patient_name"] = patient["patient_name"]
                state["patient_data"] = patient
                state["stage"] = "patient_identified"
                
                response = f"Great to see you, {patient['patient_name']}! 👋\n\n"
                response += f"I've pulled up your discharge report from {patient['discharge_date']}. I see you were treated for {patient['primary_diagnosis']}.\n\n"
                response += f"Let me share what's important for your recovery:\n\n"
                response += f"💊 **Your Medications:**\n"
                for med in patient['medications']:
                    response += f"   • {med}\n"
                response += f"\n🥗 **Diet to Follow:** {patient['dietary_restrictions']}\n"
                response += f"\n📅 **Your Next Appointment:** {patient['follow_up']}\n\n"
                response += "So, how have you been feeling since you got home? Any concerns about your medications or anything else I can help with?"
                agent = "Receptionist Agent"
                
                system_logger.log_database_access(
                    operation="SELECT",
                    table="patients",
                    query=patient_name,
                    result=f"Found patient: {patient_name}",
                    success=True
                )
            else:
                response = f"Hmm, I'm not finding '{patient_name}' in our records. Could you double-check the spelling for me?\n\nJust to help, some of our patients include John Smith, Sarah Johnson, Michael Chen, and Emily Rodriguez. Does any of those sound right?"
                agent = "Receptionist Agent"
                state["stage"] = "awaiting_name"  # Stay in same stage
        
        # STAGE 3: Handle follow-up questions (Route to Clinical Agent for medical queries)
        elif state["stage"] == "patient_identified":
            patient = state["patient_data"]
            
            # Check if it's a medical question
            medical_keywords = ["swelling", "pain", "worried", "symptom", "medication", "treatment", "kidney", "disease", "research", "study"]
            is_medical_query = any(keyword in user_message for keyword in medical_keywords)
            
            if is_medical_query:
                # Route to Clinical Agent
                agent = "Clinical AI Agent"
                
                # Simulate RAG response based on patient condition
                if "swelling" in user_message:
                    response = f"I understand your concern about the leg swelling. Let me help you understand what might be happening.\n\n"
                    response += f"With {patient['primary_diagnosis']}, leg swelling is actually quite common. It usually happens when your body retains extra fluid and sodium. Think of it like water pooling in your legs because your kidneys aren't filtering as efficiently as they should.\n\n"
                    response += f"📚 **Here's what the medical guidelines tell us:**\n"
                    response += f"For patients like you, managing swelling involves a few key things:\n"
                    response += f"   • Sticking to your fluid limits ({patient['dietary_restrictions']})\n"
                    response += f"   • Keeping sodium intake low\n"
                    response += f"   • Weighing yourself daily to track changes\n"
                    response += f"   • Taking your diuretic medication as prescribed\n\n"
                    response += f"💊 Speaking of which, I see you're taking {patient['medications'][1] if len(patient['medications']) > 1 else 'diuretic medication'}. That's actually designed to help your body get rid of excess fluid, which should help with the swelling.\n\n"
                    response += f"⚠️ **When to call your doctor right away:**\n{patient['warning_signs']}\n\n"
                    response += f"If your swelling is new, getting worse, or you're having trouble breathing, don't wait—call your healthcare provider immediately.\n\n"
                    response += f"💙 *Remember, I'm here to provide information, but your doctor knows your specific situation best. Always reach out to them with concerns.*"
                    
                    system_logger.log_agent_handoff(
                        from_agent="Receptionist Agent",
                        to_agent="Clinical AI Agent",
                        reason="Medical query about symptoms"
                    )
                    system_logger.log_rag_retrieval(
                        query=message.message,
                        num_results=3,
                        sources=["nephrology_reference.txt"],
                        success=True
                    )
                
                elif "research" in user_message or "study" in user_message or "latest" in user_message:
                    # Simulate web search
                    response = f"Great question! SGLT2 inhibitors are actually one of the most exciting developments in kidney disease treatment. Let me find the latest research for you...\n\n"
                    response += f"🔬 **Here's what recent studies are showing:**\n\n"
                    response += f"The research is really promising! There have been some major clinical trials:\n\n"
                    response += f"**DAPA-CKD Trial (2020):** This study found that dapagliflozin significantly slowed down kidney disease progression. Patients taking it had better outcomes compared to those who didn't.\n\n"
                    response += f"**CREDENCE Study:** Another big one—canagliflozin reduced the risk of kidney failure by about 30%. That's a substantial improvement!\n\n"
                    response += f"**Current Medical Guidelines:** Because of these results, SGLT2 inhibitors are now recommended for CKD patients, especially those with diabetes.\n\n"
                    response += f"💭 **What this means for you:**\n"
                    response += f"Given your {patient['primary_diagnosis']}, these medications could potentially be beneficial. However, every patient is different, and your nephrologist will need to evaluate if they're right for your specific situation.\n\n"
                    response += f"I'd suggest bringing this up at your next appointment on {patient['follow_up']}. Your doctor can discuss whether adding an SGLT2 inhibitor to your treatment plan makes sense.\n\n"
                    response += f"🌐 *Based on recent medical literature and clinical trials*\n\n"
                    response += f"💙 *This is educational information to help you have informed conversations with your healthcare team.*"
                    
                    system_logger.log_web_search(
                        query=message.message,
                        search_engine="simulated",
                        num_results=3,
                        success=True
                    )
                
                else:
                    # General medical response
                    response = f"I'm glad you're asking about this! Let me share some guidance based on your condition.\n\n"
                    response += f"For managing {patient['primary_diagnosis']}, here are the key things to focus on:\n\n"
                    response += f"   • **Stay consistent with your medications** - They're working behind the scenes to protect your kidneys\n"
                    response += f"   • **Follow your diet plan** - What you eat really does make a difference\n"
                    response += f"   • **Keep track of how you're feeling** - Notice any changes and report them\n"
                    response += f"   • **Make healthy lifestyle choices** - Small changes add up over time\n\n"
                    response += f"Your doctor specifically mentioned: {patient['discharge_instructions']}\n\n"
                    response += f"Is there anything specific you'd like to know more about? I'm here to help! 💙"
            
            else:
                # General follow-up from Receptionist
                agent = "Receptionist Agent"
                response = f"That's wonderful to hear! 😊\n\n"
                response += f"Just a friendly reminder of the important things:\n\n"
                response += f"   • {patient['discharge_instructions']}\n"
                response += f"   • Keep an eye out for: {patient['warning_signs']}\n"
                response += f"   • Don't forget your appointment: {patient['follow_up']}\n\n"
                response += f"If you have any medical questions or something's worrying you, just let me know. I'm here to help!"
        
        else:
            response = "I'm here to help! How can I assist you today?"
            agent = "Receptionist Agent"
        
        system_logger.log_interaction(
            interaction_type="agent_response",
            agent=agent,
            message=response,
            metadata={"session_id": session_id}
        )
        
        return ChatResponse(
            response=response,
            session_id=session_id,
            agent=agent,
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        system_logger.log_error("ChatError", f"Error processing chat: {str(e)}")
        raise HTTPException(status_code=500, detail="Error processing message")


@app.post("/reset")
async def reset_session(session_id: str):
    """Reset a conversation session."""
    if session_id in conversation_state:
        del conversation_state[session_id]
    return {"message": "Session reset successfully"}


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


@app.post("/patient/report/pdf")
async def download_patient_report(query: PatientQuery):
    """Generate and download patient discharge report as PDF."""
    try:
        # Get patient data
        patient = db_manager.get_patient_by_name(query.patient_name)
        if patient is None:
            raise HTTPException(status_code=404, detail="Patient not found")
        
        # Generate PDF
        pdf_bytes = generate_patient_pdf(patient)
        
        # Create filename
        safe_name = patient['patient_name'].replace(' ', '_')
        filename = f"discharge_report_{safe_name}_{datetime.now().strftime('%Y%m%d')}.pdf"
        
        # Log the action
        system_logger.info(f"Generated PDF report for patient: {patient['patient_name']}")
        
        # Return PDF as response
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        system_logger.log_error("PDFGenerationError", str(e))
        raise HTTPException(status_code=500, detail=f"Error generating PDF: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
