"""
Comprehensive logging system for the Post Discharge Medical AI Assistant.
Tracks all interactions, agent handoffs, and system decisions.
"""

from loguru import logger
import sys
from pathlib import Path
from datetime import datetime
import json
from typing import Dict, Any, Optional


class SystemLogger:
    """
    Centralized logging system for the application.
    Provides structured logging with timestamps and context.
    """
    
    def __init__(self, log_file_path: str = "./logs/system.log"):
        """
        Initialize the logging system.
        
        Args:
            log_file_path: Path to the log file
        """
        self.log_file_path = Path(log_file_path)
        self.log_file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Remove default logger
        logger.remove()
        
        # Add console logger with color
        logger.add(
            sys.stdout,
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
            level="INFO",
            colorize=True
        )
        
        # Add file logger with rotation
        logger.add(
            self.log_file_path,
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function} - {message}",
            level="DEBUG",
            rotation="10 MB",
            retention="30 days",
            compression="zip"
        )
        
        # Create interaction log file
        self.interaction_log_path = self.log_file_path.parent / "interactions.jsonl"
        
    def log_interaction(
        self,
        interaction_type: str,
        agent: str,
        message: str,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Log a user-agent interaction.
        
        Args:
            interaction_type: Type of interaction (user_input, agent_response, etc.)
            agent: Name of the agent
            message: The message content
            metadata: Additional metadata
        """
        interaction_data = {
            "timestamp": datetime.now().isoformat(),
            "type": interaction_type,
            "agent": agent,
            "message": message,
            "metadata": metadata or {}
        }
        
        # Log to console/file
        logger.info(f"[{interaction_type}] {agent}: {message}")
        
        # Log to interaction file
        with open(self.interaction_log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(interaction_data) + "\n")
    
    def log_agent_handoff(
        self,
        from_agent: str,
        to_agent: str,
        reason: str,
        context: Optional[Dict[str, Any]] = None
    ):
        """
        Log an agent handoff event.
        
        Args:
            from_agent: Source agent
            to_agent: Destination agent
            reason: Reason for handoff
            context: Additional context
        """
        handoff_data = {
            "timestamp": datetime.now().isoformat(),
            "type": "agent_handoff",
            "from_agent": from_agent,
            "to_agent": to_agent,
            "reason": reason,
            "context": context or {}
        }
        
        logger.warning(f"AGENT HANDOFF: {from_agent} -> {to_agent} | Reason: {reason}")
        
        with open(self.interaction_log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(handoff_data) + "\n")
    
    def log_database_access(
        self,
        operation: str,
        table: str,
        query: str,
        result: Optional[str] = None,
        success: bool = True
    ):
        """
        Log database access attempts.
        
        Args:
            operation: Type of operation (SELECT, INSERT, etc.)
            table: Table name
            query: Query or search term
            result: Result summary
            success: Whether operation succeeded
        """
        db_data = {
            "timestamp": datetime.now().isoformat(),
            "type": "database_access",
            "operation": operation,
            "table": table,
            "query": query,
            "result": result,
            "success": success
        }
        
        status = "SUCCESS" if success else "FAILED"
        logger.info(f"DB ACCESS [{status}]: {operation} on {table} - Query: {query}")
        
        with open(self.interaction_log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(db_data) + "\n")
    
    def log_rag_retrieval(
        self,
        query: str,
        num_results: int,
        sources: list,
        success: bool = True
    ):
        """
        Log RAG retrieval attempts.
        
        Args:
            query: Search query
            num_results: Number of results retrieved
            sources: List of source documents
            success: Whether retrieval succeeded
        """
        rag_data = {
            "timestamp": datetime.now().isoformat(),
            "type": "rag_retrieval",
            "query": query,
            "num_results": num_results,
            "sources": sources,
            "success": success
        }
        
        logger.info(f"RAG RETRIEVAL: Query='{query}' | Results={num_results} | Sources={len(sources)}")
        
        with open(self.interaction_log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(rag_data) + "\n")
    
    def log_web_search(
        self,
        query: str,
        search_engine: str,
        num_results: int,
        success: bool = True
    ):
        """
        Log web search attempts.
        
        Args:
            query: Search query
            search_engine: Search engine used
            num_results: Number of results
            success: Whether search succeeded
        """
        search_data = {
            "timestamp": datetime.now().isoformat(),
            "type": "web_search",
            "query": query,
            "search_engine": search_engine,
            "num_results": num_results,
            "success": success
        }
        
        logger.info(f"WEB SEARCH [{search_engine}]: Query='{query}' | Results={num_results}")
        
        with open(self.interaction_log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(search_data) + "\n")
    
    def log_error(
        self,
        error_type: str,
        error_message: str,
        context: Optional[Dict[str, Any]] = None
    ):
        """
        Log error events.
        
        Args:
            error_type: Type of error
            error_message: Error message
            context: Additional context
        """
        error_data = {
            "timestamp": datetime.now().isoformat(),
            "type": "error",
            "error_type": error_type,
            "error_message": error_message,
            "context": context or {}
        }
        
        logger.error(f"ERROR [{error_type}]: {error_message}")
        
        with open(self.interaction_log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(error_data) + "\n")
    
    def info(self, message: str):
        """Log info message."""
        logger.info(message)
    
    def debug(self, message: str):
        """Log debug message."""
        logger.debug(message)
    
    def warning(self, message: str):
        """Log warning message."""
        logger.warning(message)
    
    def error(self, message: str):
        """Log error message."""
        logger.error(message)


# Global logger instance
system_logger = SystemLogger()
