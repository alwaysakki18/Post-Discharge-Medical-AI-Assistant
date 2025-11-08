"""
Receptionist Agent - Handles patient identification and initial interactions.
"""

from typing import TypedDict, Annotated, Sequence
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder

from ..tools.patient_retrieval import create_patient_retrieval_tool
from ..utils.logger import system_logger
from ..config import settings


class ReceptionistAgent:
    """
    Receptionist Agent responsible for:
    - Greeting patients
    - Asking for patient name
    - Retrieving discharge reports
    - Asking follow-up questions based on discharge info
    - Routing medical queries to Clinical Agent
    """
    
    def __init__(self):
        """Initialize the Receptionist Agent."""
        self.name = "Receptionist Agent"
        
        # Initialize LLM
        self.llm = ChatOpenAI(
            model=settings.llm_model,
            temperature=0.7,
            api_key=settings.openai_api_key
        )
        
        # Initialize tools
        self.tools = [create_patient_retrieval_tool()]
        
        # Create prompt
        self.prompt = self._create_prompt()
        
        # Create agent
        self.agent = create_openai_functions_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=self.prompt
        )
        
        # Create agent executor
        self.agent_executor = AgentExecutor(
            agent=self.agent,
            tools=self.tools,
            verbose=True,
            handle_parsing_errors=True,
            max_iterations=3
        )
        
        system_logger.info("Receptionist Agent initialized")
    
    def _create_prompt(self) -> ChatPromptTemplate:
        """Create the agent prompt."""
        system_message = """You are a friendly and professional Receptionist Agent for a post-discharge medical care system.

Your responsibilities:
1. Greet patients warmly and professionally
2. Ask for the patient's name if not provided
3. Use the patient_data_retrieval tool to fetch their discharge report
4. Review the discharge information and ask relevant follow-up questions about:
   - How they are feeling
   - Medication adherence
   - Dietary compliance
   - Any concerning symptoms
5. Identify when a patient has a MEDICAL QUESTION that requires clinical expertise
6. Route medical questions to the Clinical Agent by clearly stating: "ROUTE_TO_CLINICAL: [patient's medical question]"

Important guidelines:
- Always be empathetic and supportive
- Use simple, clear language
- After retrieving discharge info, ask 2-3 relevant follow-up questions
- If patient mentions symptoms from their warning signs list, immediately route to Clinical Agent
- For general questions about medications, diet, or symptoms, route to Clinical Agent
- Keep track of the conversation context
- Never provide medical advice - that's the Clinical Agent's role

Medical Disclaimer: Remind patients that this is an AI assistant for educational purposes only and they should always consult healthcare professionals for medical advice.

When you determine a medical question needs clinical expertise, respond with:
"ROUTE_TO_CLINICAL: [the patient's question]"
"""
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_message),
            MessagesPlaceholder(variable_name="chat_history", optional=True),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad")
        ])
        
        return prompt
    
    def process_message(
        self,
        message: str,
        chat_history: list = None
    ) -> dict:
        """
        Process a user message.
        
        Args:
            message: User's message
            chat_history: Previous conversation history
            
        Returns:
            Dictionary with response and routing information
        """
        try:
            system_logger.log_interaction(
                interaction_type="user_input",
                agent=self.name,
                message=message
            )
            
            # Prepare input
            agent_input = {
                "input": message,
                "chat_history": chat_history or []
            }
            
            # Execute agent
            result = self.agent_executor.invoke(agent_input)
            response = result.get("output", "")
            
            # Check if routing to clinical agent
            should_route = "ROUTE_TO_CLINICAL:" in response
            clinical_query = None
            
            if should_route:
                # Extract the clinical query
                parts = response.split("ROUTE_TO_CLINICAL:")
                if len(parts) > 1:
                    clinical_query = parts[1].strip()
                    # Remove routing instruction from response
                    response = parts[0].strip()
                    if not response:
                        response = "Let me connect you with our Clinical AI Agent who can better address your medical question."
            
            system_logger.log_interaction(
                interaction_type="agent_response",
                agent=self.name,
                message=response,
                metadata={"should_route": should_route, "clinical_query": clinical_query}
            )
            
            return {
                "response": response,
                "should_route_to_clinical": should_route,
                "clinical_query": clinical_query,
                "agent": "receptionist"
            }
            
        except Exception as e:
            error_msg = f"Error in Receptionist Agent: {str(e)}"
            system_logger.log_error("ReceptionistAgentError", error_msg)
            return {
                "response": "I apologize, but I encountered an error. Please try again.",
                "should_route_to_clinical": False,
                "clinical_query": None,
                "agent": "receptionist"
            }
    
    def should_route_to_clinical(self, message: str) -> bool:
        """
        Determine if message should be routed to clinical agent.
        
        Args:
            message: User's message
            
        Returns:
            True if should route to clinical agent
        """
        # Keywords that indicate medical questions
        medical_keywords = [
            "pain", "swelling", "symptom", "medication", "side effect",
            "treatment", "diagnosis", "test", "result", "worried",
            "concerned", "should i", "what if", "is it normal",
            "blood pressure", "kidney", "urine", "breathing",
            "chest", "heart", "fever", "infection"
        ]
        
        message_lower = message.lower()
        return any(keyword in message_lower for keyword in medical_keywords)


def create_receptionist_agent() -> ReceptionistAgent:
    """
    Create and return a Receptionist Agent instance.
    
    Returns:
        ReceptionistAgent instance
    """
    return ReceptionistAgent()
