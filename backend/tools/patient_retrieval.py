"""
Patient data retrieval tool for the Receptionist Agent.
"""

from typing import Optional, Dict, Any
from langchain.tools import Tool
from pydantic import BaseModel, Field

from ..database.database import get_db_manager
from ..utils.logger import system_logger


class PatientRetrievalInput(BaseModel):
    """Input schema for patient retrieval tool."""
    patient_name: str = Field(description="The name of the patient to retrieve")


class PatientRetrievalTool:
    """
    Tool for retrieving patient discharge reports from the database.
    Used by the Receptionist Agent to fetch patient information.
    """
    
    def __init__(self):
        """Initialize the patient retrieval tool."""
        self.db_manager = get_db_manager()
        self.name = "patient_data_retrieval"
        self.description = """
        Retrieves a patient's discharge report from the database by name.
        Use this tool when a patient provides their name to fetch their discharge information.
        Input should be the patient's name as a string.
        Returns the complete discharge report including diagnosis, medications, dietary restrictions, etc.
        """
    
    def retrieve_patient(self, patient_name: str) -> str:
        """
        Retrieve patient data by name.
        
        Args:
            patient_name: Patient's name
            
        Returns:
            Formatted patient information or error message
        """
        try:
            system_logger.info(f"Retrieving patient data for: {patient_name}")
            
            # Get patient from database
            patient_data = self.db_manager.get_patient_by_name(patient_name)
            
            if patient_data is None:
                # Try searching for similar names
                search_results = self.db_manager.search_patients(patient_name)
                
                if len(search_results) == 0:
                    return f"I couldn't find a patient named '{patient_name}' in our system. Please check the spelling or provide the full name."
                elif len(search_results) == 1:
                    patient_data = search_results[0]
                    system_logger.info(f"Found patient through search: {patient_data['patient_name']}")
                else:
                    # Multiple matches
                    names = [p['patient_name'] for p in search_results]
                    return f"I found multiple patients with similar names: {', '.join(names)}. Please specify the full name."
            
            # Format patient information
            formatted_info = self._format_patient_info(patient_data)
            
            system_logger.log_database_access(
                operation="RETRIEVE",
                table="patients",
                query=patient_name,
                result=f"Successfully retrieved: {patient_data['patient_name']}",
                success=True
            )
            
            return formatted_info
            
        except Exception as e:
            error_msg = f"Error retrieving patient data: {str(e)}"
            system_logger.log_error("PatientRetrievalError", error_msg, {"patient_name": patient_name})
            return f"I encountered an error while retrieving the patient data. Please try again."
    
    def _format_patient_info(self, patient_data: Dict[str, Any]) -> str:
        """
        Format patient data into a readable string.
        
        Args:
            patient_data: Patient data dictionary
            
        Returns:
            Formatted patient information
        """
        medications_list = "\n  - ".join(patient_data.get('medications', []))
        
        formatted = f"""
Patient Discharge Report Retrieved:

Patient Name: {patient_data.get('patient_name')}
Discharge Date: {patient_data.get('discharge_date')}
Primary Diagnosis: {patient_data.get('primary_diagnosis')}

Medications:
  - {medications_list}

Dietary Restrictions: {patient_data.get('dietary_restrictions')}

Follow-up: {patient_data.get('follow_up')}

Warning Signs to Watch For: {patient_data.get('warning_signs')}

Discharge Instructions: {patient_data.get('discharge_instructions')}
"""
        return formatted.strip()
    
    def as_langchain_tool(self) -> Tool:
        """
        Convert to LangChain Tool.
        
        Returns:
            LangChain Tool instance
        """
        return Tool(
            name=self.name,
            description=self.description,
            func=self.retrieve_patient
        )


def create_patient_retrieval_tool() -> Tool:
    """
    Create and return a patient retrieval tool.
    
    Returns:
        LangChain Tool for patient retrieval
    """
    tool = PatientRetrievalTool()
    return tool.as_langchain_tool()
