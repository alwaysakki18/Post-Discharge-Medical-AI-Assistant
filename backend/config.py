"""
Configuration module for the Post Discharge Medical AI Assistant.
Handles environment variables and application settings.
"""

from pydantic_settings import BaseSettings
from typing import Optional
import os
from pathlib import Path


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # API Keys
    openai_api_key: str
    tavily_api_key: Optional[str] = None
    
    # Application Settings
    environment: str = "development"
    log_level: str = "INFO"
    
    # Database Configuration
    database_path: str = "./data/patients.db"
    
    # Vector Database Configuration
    vector_db_path: str = "./data/vector_db"
    
    # Model Configuration
    llm_model: str = "gpt-4-turbo-preview"
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    temperature: float = 0.7
    
    # RAG Configuration
    chunk_size: int = 1000
    chunk_overlap: int = 200
    top_k_results: int = 5
    
    # Logging
    log_file_path: str = "./logs/system.log"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Initialize settings
settings = Settings()

# Create necessary directories
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
LOGS_DIR = BASE_DIR / "logs"
VECTOR_DB_DIR = BASE_DIR / "data" / "vector_db"

# Ensure directories exist
DATA_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)
VECTOR_DB_DIR.mkdir(parents=True, exist_ok=True)
