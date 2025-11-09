"""
RAG tool for retrieving information from nephrology reference materials.
"""

from typing import List, Dict, Any
from langchain.tools import Tool
from pydantic import BaseModel, Field

from ..rag.vector_store_openai import get_vector_store
from ..utils.logger import system_logger


class RAGInput(BaseModel):
    """Input schema for RAG tool."""
    query: str = Field(description="The medical query to search in nephrology reference materials")


class RAGTool:
    """
    Tool for retrieving information from nephrology reference materials
    using Retrieval-Augmented Generation (RAG).
    """
    
    def __init__(self, top_k: int = 5):
        """
        Initialize the RAG tool.
        
        Args:
            top_k: Number of relevant chunks to retrieve
        """
        self.vector_store = get_vector_store()
        self.top_k = top_k
        self.name = "nephrology_knowledge_base"
        self.description = """
        Searches the nephrology reference materials for relevant medical information.
        Use this tool to answer medical questions about:
        - Chronic Kidney Disease (CKD) and staging
        - Acute Kidney Injury (AKI)
        - Diabetic Nephropathy
        - Glomerular diseases (nephrotic/nephritic syndrome)
        - Hypertension and kidney disease
        - Electrolyte disorders
        - CKD-Mineral and Bone Disorder
        - Anemia in CKD
        - Polycystic Kidney Disease
        - Lupus Nephritis
        - Kidney stones
        - Medication management in CKD
        - Dialysis
        - Kidney transplantation
        
        Input should be a clear medical question or query.
        Returns relevant information with source citations.
        """
    
    def retrieve(self, query: str) -> str:
        """
        Retrieve relevant information from nephrology knowledge base.
        
        Args:
            query: Medical query
            
        Returns:
            Formatted response with citations
        """
        try:
            system_logger.info(f"RAG query: {query}")
            
            # Perform similarity search
            results = self.vector_store.similarity_search(
                query=query,
                k=self.top_k
            )
            
            if not results:
                return "I couldn't find specific information about this in the nephrology reference materials. Would you like me to search the web for more current information?"
            
            # Format response with citations
            formatted_response = self._format_response(results, query)
            
            return formatted_response
            
        except Exception as e:
            error_msg = f"Error retrieving from knowledge base: {str(e)}"
            system_logger.log_error("RAGError", error_msg, {"query": query})
            return "I encountered an error while searching the nephrology reference materials. Please try rephrasing your question."
    
    def _format_response(self, results: List[Dict[str, Any]], query: str) -> str:
        """
        Format RAG results with citations.
        
        Args:
            results: List of retrieved documents
            query: Original query
            
        Returns:
            Formatted response string
        """
        formatted = f"\n📚 Information from Nephrology Reference Materials:\n"
        formatted += "=" * 60 + "\n\n"
        
        # Combine relevant chunks
        combined_content = []
        sources = set()
        
        for i, result in enumerate(results):
            content = result['content']
            metadata = result.get('metadata', {})
            source = metadata.get('source', 'Unknown')
            chunk_id = metadata.get('chunk_id', i)
            
            combined_content.append(content)
            sources.add(source)
        
        # Join content
        formatted += "\n\n".join(combined_content)
        
        # Add citations
        formatted += "\n\n" + "=" * 60 + "\n"
        formatted += "📖 Sources:\n"
        for source in sources:
            formatted += f"  - {source}\n"
        
        formatted += "\n⚕️ This information is from medical reference materials. Always consult with your healthcare provider for personalized medical advice.\n"
        
        return formatted
    
    def get_relevant_chunks(self, query: str) -> List[str]:
        """
        Get relevant text chunks without formatting.
        
        Args:
            query: Medical query
            
        Returns:
            List of relevant text chunks
        """
        try:
            results = self.vector_store.similarity_search(
                query=query,
                k=self.top_k
            )
            return [r['content'] for r in results]
        except Exception as e:
            system_logger.log_error("RAGError", f"Error getting chunks: {str(e)}")
            return []
    
    def as_langchain_tool(self) -> Tool:
        """
        Convert to LangChain Tool.
        
        Returns:
            LangChain Tool instance
        """
        return Tool(
            name=self.name,
            description=self.description,
            func=self.retrieve
        )


def create_rag_tool(top_k: int = 5) -> Tool:
    """
    Create and return a RAG tool.
    
    Args:
        top_k: Number of relevant chunks to retrieve
        
    Returns:
        LangChain Tool for RAG
    """
    tool = RAGTool(top_k=top_k)
    return tool.as_langchain_tool()
