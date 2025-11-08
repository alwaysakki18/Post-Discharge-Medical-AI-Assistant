"""
Database connection and operations.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from typing import Optional, List
import json
from pathlib import Path

from .models import Base, Patient, Interaction
from ..utils.logger import system_logger


class DatabaseManager:
    """Manages database connections and operations."""
    
    def __init__(self, database_url: str = "sqlite:///./data/patients.db"):
        """
        Initialize database manager.
        
        Args:
            database_url: SQLAlchemy database URL
        """
        self.database_url = database_url
        
        # Create engine
        self.engine = create_engine(
            database_url,
            connect_args={"check_same_thread": False},
            poolclass=StaticPool
        )
        
        # Create tables
        Base.metadata.create_all(bind=self.engine)
        
        # Create session factory
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        
        system_logger.info(f"Database initialized: {database_url}")
    
    def get_session(self) -> Session:
        """Get a new database session."""
        return self.SessionLocal()
    
    def load_patient_data(self, json_file_path: str):
        """
        Load patient data from JSON file into database.
        
        Args:
            json_file_path: Path to JSON file with patient data
        """
        session = self.get_session()
        try:
            # Check if data already loaded
            count = session.query(Patient).count()
            if count > 0:
                system_logger.info(f"Database already contains {count} patients. Skipping load.")
                return
            
            # Load JSON data
            with open(json_file_path, 'r', encoding='utf-8') as f:
                patients_data = json.load(f)
            
            # Insert patients
            for patient_data in patients_data:
                patient = Patient(
                    patient_id=patient_data['patient_id'],
                    patient_name=patient_data['patient_name'],
                    discharge_date=patient_data['discharge_date'],
                    primary_diagnosis=patient_data['primary_diagnosis'],
                    medications=patient_data['medications'],
                    dietary_restrictions=patient_data['dietary_restrictions'],
                    follow_up=patient_data['follow_up'],
                    warning_signs=patient_data['warning_signs'],
                    discharge_instructions=patient_data['discharge_instructions']
                )
                session.add(patient)
            
            session.commit()
            system_logger.info(f"Loaded {len(patients_data)} patients into database")
            
        except Exception as e:
            session.rollback()
            system_logger.error(f"Error loading patient data: {str(e)}")
            raise
        finally:
            session.close()
    
    def get_patient_by_name(self, patient_name: str) -> Optional[dict]:
        """
        Retrieve patient by name.
        
        Args:
            patient_name: Patient's name
            
        Returns:
            Patient data dictionary or None
        """
        session = self.get_session()
        try:
            # Case-insensitive search
            patient = session.query(Patient).filter(
                Patient.patient_name.ilike(f"%{patient_name}%")
            ).first()
            
            if patient:
                system_logger.log_database_access(
                    operation="SELECT",
                    table="patients",
                    query=patient_name,
                    result=f"Found patient: {patient.patient_name}",
                    success=True
                )
                return patient.to_dict()
            else:
                system_logger.log_database_access(
                    operation="SELECT",
                    table="patients",
                    query=patient_name,
                    result="Patient not found",
                    success=False
                )
                return None
                
        except Exception as e:
            system_logger.log_error("DatabaseError", str(e), {"patient_name": patient_name})
            return None
        finally:
            session.close()
    
    def get_all_patients(self) -> List[dict]:
        """
        Get all patients.
        
        Returns:
            List of patient dictionaries
        """
        session = self.get_session()
        try:
            patients = session.query(Patient).all()
            return [p.to_dict() for p in patients]
        except Exception as e:
            system_logger.log_error("DatabaseError", str(e))
            return []
        finally:
            session.close()
    
    def search_patients(self, search_term: str) -> List[dict]:
        """
        Search patients by name or diagnosis.
        
        Args:
            search_term: Search term
            
        Returns:
            List of matching patient dictionaries
        """
        session = self.get_session()
        try:
            patients = session.query(Patient).filter(
                (Patient.patient_name.ilike(f"%{search_term}%")) |
                (Patient.primary_diagnosis.ilike(f"%{search_term}%"))
            ).all()
            
            system_logger.log_database_access(
                operation="SEARCH",
                table="patients",
                query=search_term,
                result=f"Found {len(patients)} patients",
                success=True
            )
            
            return [p.to_dict() for p in patients]
        except Exception as e:
            system_logger.log_error("DatabaseError", str(e), {"search_term": search_term})
            return []
        finally:
            session.close()
    
    def log_interaction(
        self,
        session_id: str,
        patient_name: str,
        agent: str,
        message_type: str,
        message: str,
        metadata: Optional[dict] = None
    ):
        """
        Log a patient interaction.
        
        Args:
            session_id: Session identifier
            patient_name: Patient's name
            agent: Agent name (receptionist/clinical)
            message_type: Type of message
            message: Message content
            metadata: Additional metadata
        """
        session = self.get_session()
        try:
            interaction = Interaction(
                session_id=session_id,
                patient_name=patient_name,
                agent=agent,
                message_type=message_type,
                message=message,
                metadata=metadata or {}
            )
            session.add(interaction)
            session.commit()
        except Exception as e:
            session.rollback()
            system_logger.log_error("DatabaseError", str(e))
        finally:
            session.close()
    
    def get_session_history(self, session_id: str) -> List[dict]:
        """
        Get interaction history for a session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            List of interaction dictionaries
        """
        session = self.get_session()
        try:
            interactions = session.query(Interaction).filter(
                Interaction.session_id == session_id
            ).order_by(Interaction.timestamp).all()
            
            return [i.to_dict() for i in interactions]
        except Exception as e:
            system_logger.log_error("DatabaseError", str(e))
            return []
        finally:
            session.close()


# Global database manager instance
db_manager = None

def get_db_manager(database_url: str = "sqlite:///./data/patients.db") -> DatabaseManager:
    """Get or create database manager instance."""
    global db_manager
    if db_manager is None:
        db_manager = DatabaseManager(database_url)
    return db_manager
