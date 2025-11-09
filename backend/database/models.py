"""
Database models for patient records and interactions.
"""

from sqlalchemy import Column, Integer, String, DateTime, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()


class Patient(Base):
    """Patient discharge report model."""
    
    __tablename__ = "patients"
    
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, unique=True, index=True)
    patient_name = Column(String, index=True)
    discharge_date = Column(String)
    primary_diagnosis = Column(String)
    medications = Column(JSON)  # List of medications
    dietary_restrictions = Column(Text)
    follow_up = Column(Text)
    warning_signs = Column(Text)
    discharge_instructions = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        """Convert patient record to dictionary."""
        return {
            "patient_id": self.patient_id,
            "patient_name": self.patient_name,
            "discharge_date": self.discharge_date,
            "primary_diagnosis": self.primary_diagnosis,
            "medications": self.medications,
            "dietary_restrictions": self.dietary_restrictions,
            "follow_up": self.follow_up,
            "warning_signs": self.warning_signs,
            "discharge_instructions": self.discharge_instructions
        }


class Interaction(Base):
    """Patient interaction log model."""
    
    __tablename__ = "interactions"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, index=True)
    patient_name = Column(String, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    agent = Column(String)  # receptionist or clinical
    message_type = Column(String)  # user_input, agent_response, handoff
    message = Column(Text)
    meta_data = Column(JSON)  # Renamed from metadata to avoid SQLAlchemy reserved word
    
    def to_dict(self):
        """Convert interaction to dictionary."""
        return {
            "id": self.id,
            "session_id": self.session_id,
            "patient_name": self.patient_name,
            "timestamp": self.timestamp.isoformat(),
            "agent": self.agent,
            "message_type": self.message_type,
            "message": self.message,
            "metadata": self.meta_data
        }
