"""
Multi-Agent Graph using LangGraph for orchestrating Receptionist and Clinical agents.
"""

from typing import TypedDict, Annotated, Literal
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, AIMessage
import uuid

from .receptionist_agent import create_receptionist_agent
from .clinical_agent import create_clinical_agent
from ..utils.logger import system_logger


class AgentState(TypedDict):
    """State for the multi-agent system."""
    messages: list
    current_agent: str
    patient_name: str
    patient_context: dict
    session_id: str
    should_route: bool
    clinical_query: str
    response: str


class MultiAgentSystem:
    """
    Multi-agent system orchestrating Receptionist and Clinical agents.
    Uses LangGraph for state management and agent routing.
    """
    
    def __init__(self):
        """Initialize the multi-agent system."""
        self.session_id = str(uuid.uuid4())
        
        # Initialize agents
        self.receptionist_agent = create_receptionist_agent()
        self.clinical_agent = create_clinical_agent()
        
        # Build graph
        self.graph = self._build_graph()
        self.app = self.graph.compile()
        
        # State
        self.state = {
            "messages": [],
            "current_agent": "receptionist",
            "patient_name": None,
            "patient_context": None,
            "session_id": self.session_id,
            "should_route": False,
            "clinical_query": None,
            "response": ""
        }
        
        system_logger.info(f"Multi-Agent System initialized with session: {self.session_id}")
    
    def _build_graph(self) -> StateGraph:
        """Build the agent graph."""
        # Create graph
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("receptionist", self._receptionist_node)
        workflow.add_node("clinical", self._clinical_node)
        
        # Add edges
        workflow.set_entry_point("receptionist")
        
        # Conditional routing from receptionist
        workflow.add_conditional_edges(
            "receptionist",
            self._route_from_receptionist,
            {
                "clinical": "clinical",
                "end": END
            }
        )
        
        # Clinical agent always ends
        workflow.add_edge("clinical", END)
        
        return workflow
    
    def _receptionist_node(self, state: AgentState) -> AgentState:
        """Process message with Receptionist Agent."""
        try:
            # Get last message
            last_message = state["messages"][-1] if state["messages"] else None
            if not last_message:
                return state
            
            user_message = last_message.content if hasattr(last_message, 'content') else str(last_message)
            
            # Get chat history
            chat_history = state["messages"][:-1] if len(state["messages"]) > 1 else []
            
            # Process with receptionist
            result = self.receptionist_agent.process_message(
                message=user_message,
                chat_history=chat_history
            )
            
            # Update state
            state["response"] = result["response"]
            state["should_route"] = result["should_route_to_clinical"]
            state["clinical_query"] = result["clinical_query"]
            state["current_agent"] = "receptionist"
            
            # Add response to messages
            state["messages"].append(AIMessage(content=result["response"]))
            
            return state
            
        except Exception as e:
            system_logger.log_error("GraphError", f"Error in receptionist node: {str(e)}")
            state["response"] = "I apologize for the error. Please try again."
            state["should_route"] = False
            return state
    
    def _clinical_node(self, state: AgentState) -> AgentState:
        """Process message with Clinical Agent."""
        try:
            # Log handoff
            system_logger.log_agent_handoff(
                from_agent="Receptionist Agent",
                to_agent="Clinical AI Agent",
                reason="Medical query requires clinical expertise",
                context={"query": state.get("clinical_query")}
            )
            
            # Get the clinical query or last message
            query = state.get("clinical_query") or (
                state["messages"][-1].content if state["messages"] else ""
            )
            
            # Get chat history
            chat_history = state["messages"][:-1] if len(state["messages"]) > 1 else []
            
            # Process with clinical agent
            result = self.clinical_agent.process_message(
                message=query,
                patient_context=state.get("patient_context"),
                chat_history=chat_history
            )
            
            # Update state
            state["response"] = result["response"]
            state["current_agent"] = "clinical"
            
            # Add response to messages
            state["messages"].append(AIMessage(content=result["response"]))
            
            return state
            
        except Exception as e:
            system_logger.log_error("GraphError", f"Error in clinical node: {str(e)}")
            state["response"] = "I apologize for the error. Please consult your healthcare provider."
            return state
    
    def _route_from_receptionist(self, state: AgentState) -> Literal["clinical", "end"]:
        """Determine routing from receptionist agent."""
        if state.get("should_route", False):
            return "clinical"
        return "end"
    
    def process_message(self, message: str) -> str:
        """
        Process a user message through the multi-agent system.
        
        Args:
            message: User's message
            
        Returns:
            Agent's response
        """
        try:
            # Add user message to state
            self.state["messages"].append(HumanMessage(content=message))
            
            # Run graph
            result = self.app.invoke(self.state)
            
            # Update state
            self.state = result
            
            # Return response
            return result.get("response", "I apologize, but I couldn't process your message.")
            
        except Exception as e:
            system_logger.log_error("MultiAgentError", f"Error processing message: {str(e)}")
            return "I apologize for the error. Please try again."
    
    def reset_session(self):
        """Reset the session."""
        self.session_id = str(uuid.uuid4())
        self.state = {
            "messages": [],
            "current_agent": "receptionist",
            "patient_name": None,
            "patient_context": None,
            "session_id": self.session_id,
            "should_route": False,
            "clinical_query": None,
            "response": ""
        }
        system_logger.info(f"Session reset: {self.session_id}")
    
    def get_conversation_history(self) -> list:
        """Get the conversation history."""
        return self.state.get("messages", [])
    
    def set_patient_context(self, patient_context: dict):
        """Set patient context for the session."""
        self.state["patient_context"] = patient_context
        self.state["patient_name"] = patient_context.get("patient_name")
        system_logger.info(f"Patient context set: {patient_context.get('patient_name')}")


def create_multi_agent_system() -> MultiAgentSystem:
    """
    Create and return a Multi-Agent System instance.
    
    Returns:
        MultiAgentSystem instance
    """
    return MultiAgentSystem()
