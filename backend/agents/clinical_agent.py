"""
Clinical AI Agent - Handles medical questions using RAG and web search.
"""

from typing import List, Dict, Any
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder

from ..tools.rag_tool import create_rag_tool
from ..tools.web_search import create_web_search_tool
from ..utils.logger import system_logger
from ..config import settings


class ClinicalAgent:
    """
    Clinical AI Agent responsible for:
    - Answering medical questions
    - Using RAG over nephrology reference materials
    - Using web search for queries outside reference materials
    - Providing citations and sources
    - Logging all interactions
    """
    
    def __init__(self):
        """Initialize the Clinical Agent."""
        self.name = "Clinical AI Agent"
        
        # Initialize LLM with lower temperature for medical accuracy
        self.llm = ChatOpenAI(
            model=settings.llm_model,
            temperature=0.3,  # Lower temperature for more consistent medical responses
            api_key=settings.openai_api_key
        )
        
        # Initialize tools
        self.tools = [
            create_rag_tool(top_k=5),
            create_web_search_tool()
        ]
        
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
            max_iterations=5
        )
        
        system_logger.info("Clinical AI Agent initialized")
    
    def _create_prompt(self) -> ChatPromptTemplate:
        """Create the agent prompt."""
        system_message = """You are a knowledgeable Clinical AI Agent specializing in nephrology and post-discharge patient care.

Your responsibilities:
1. Answer medical questions accurately and professionally
2. Use the nephrology_knowledge_base tool FIRST to search reference materials
3. If information is not in reference materials or patient asks about recent research, use the web_search tool
4. Always provide citations and sources for your information
5. Explain medical concepts in clear, patient-friendly language
6. Acknowledge limitations and recommend consulting healthcare providers when appropriate

Tool Usage Guidelines:
- ALWAYS try nephrology_knowledge_base FIRST for medical questions
- Use web_search for:
  * Recent research or clinical trials
  * New medications or treatments
  * Information not covered in reference materials
  * Current guidelines or recommendations
- Clearly indicate the source of information (reference materials vs. web search)

Response Guidelines:
- Be empathetic and supportive
- Use simple language, avoid excessive medical jargon
- When using medical terms, provide brief explanations
- Structure responses clearly with bullet points or sections when appropriate
- Always include relevant warnings or precautions
- Emphasize when symptoms require immediate medical attention

Important Disclaimers:
- Always remind patients this is educational information only
- Encourage patients to consult their healthcare provider for personalized advice
- Never diagnose conditions or prescribe treatments
- For emergencies, advise calling emergency services

Context Awareness:
- Consider the patient's discharge diagnosis when answering
- Reference their specific medications or restrictions when relevant
- Be mindful of their warning signs and follow-up schedule

Medical Disclaimer: "⚕️ This is an AI assistant for educational purposes only. Always consult healthcare professionals for medical advice."
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
        patient_context: Dict[str, Any] = None,
        chat_history: list = None
    ) -> dict:
        """
        Process a medical query.
        
        Args:
            message: User's medical question
            patient_context: Patient's discharge information for context
            chat_history: Previous conversation history
            
        Returns:
            Dictionary with response and metadata
        """
        try:
            system_logger.log_interaction(
                interaction_type="user_input",
                agent=self.name,
                message=message,
                metadata={"has_patient_context": patient_context is not None}
            )
            
            # Enhance message with patient context if available
            enhanced_message = message
            if patient_context:
                context_info = f"\n\nPatient Context:\n"
                context_info += f"- Diagnosis: {patient_context.get('primary_diagnosis', 'Unknown')}\n"
                context_info += f"- Medications: {', '.join(patient_context.get('medications', []))}\n"
                context_info += f"- Dietary Restrictions: {patient_context.get('dietary_restrictions', 'None specified')}\n"
                enhanced_message = message + context_info
            
            # Prepare input
            agent_input = {
                "input": enhanced_message,
                "chat_history": chat_history or []
            }
            
            # Execute agent
            result = self.agent_executor.invoke(agent_input)
            response = result.get("output", "")
            
            # Ensure medical disclaimer is included
            if "⚕️" not in response and "medical advice" not in response.lower():
                response += "\n\n⚕️ This is an AI assistant for educational purposes only. Always consult healthcare professionals for medical advice."
            
            system_logger.log_interaction(
                interaction_type="agent_response",
                agent=self.name,
                message=response,
                metadata={"patient_context_used": patient_context is not None}
            )
            
            return {
                "response": response,
                "agent": "clinical",
                "used_patient_context": patient_context is not None
            }
            
        except Exception as e:
            error_msg = f"Error in Clinical Agent: {str(e)}"
            system_logger.log_error("ClinicalAgentError", error_msg)
            return {
                "response": "I apologize, but I encountered an error while processing your medical question. Please consult your healthcare provider directly.",
                "agent": "clinical",
                "error": str(e)
            }
    
    def get_emergency_response(self, symptoms: List[str]) -> str:
        """
        Generate emergency response for severe symptoms.
        
        Args:
            symptoms: List of symptoms
            
        Returns:
            Emergency response message
        """
        response = "🚨 IMPORTANT: Based on your symptoms, you may need immediate medical attention.\n\n"
        response += "Please consider:\n"
        response += "1. Call your doctor immediately\n"
        response += "2. Go to the emergency room if symptoms are severe\n"
        response += "3. Call emergency services (911) if you have:\n"
        response += "   - Severe chest pain\n"
        response += "   - Difficulty breathing\n"
        response += "   - Severe confusion or loss of consciousness\n"
        response += "   - Severe bleeding\n\n"
        response += "⚕️ This is an AI assistant and cannot replace emergency medical care."
        
        return response


def create_clinical_agent() -> ClinicalAgent:
    """
    Create and return a Clinical Agent instance.
    
    Returns:
        ClinicalAgent instance
    """
    return ClinicalAgent()
