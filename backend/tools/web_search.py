"""
Web search tool for the Clinical Agent.
Provides fallback for queries outside reference materials.
"""

from typing import Optional, List, Dict, Any
from langchain.tools import Tool
from pydantic import BaseModel, Field
import os

from ..utils.logger import system_logger


class WebSearchInput(BaseModel):
    """Input schema for web search tool."""
    query: str = Field(description="The search query")


class WebSearchTool:
    """
    Tool for performing web searches when information is not available
    in the nephrology reference materials.
    """
    
    def __init__(self):
        """Initialize the web search tool."""
        self.name = "web_search"
        self.description = """
        Searches the web for medical information not found in the nephrology reference materials.
        Use this tool when:
        1. The patient asks about recent research or treatments
        2. The query is outside the scope of nephrology reference materials
        3. You need current information about medications or procedures
        
        Input should be a clear, specific search query.
        Returns relevant web search results with sources.
        """
        
        # Try to use Tavily if API key is available, otherwise use DuckDuckGo
        self.search_engine = self._initialize_search_engine()
    
    def _initialize_search_engine(self):
        """Initialize the appropriate search engine."""
        tavily_api_key = os.getenv("TAVILY_API_KEY")
        
        if tavily_api_key:
            try:
                from langchain_community.tools.tavily_search import TavilySearchResults
                system_logger.info("Initializing Tavily search engine")
                return TavilySearchResults(
                    max_results=5,
                    search_depth="advanced",
                    include_answer=True,
                    include_raw_content=False
                )
            except Exception as e:
                system_logger.warning(f"Failed to initialize Tavily: {e}. Falling back to DuckDuckGo")
        
        # Fallback to DuckDuckGo
        try:
            from langchain_community.tools import DuckDuckGoSearchResults
            system_logger.info("Initializing DuckDuckGo search engine")
            return DuckDuckGoSearchResults(max_results=5)
        except Exception as e:
            system_logger.error(f"Failed to initialize DuckDuckGo: {e}")
            return None
    
    def search(self, query: str) -> str:
        """
        Perform web search.
        
        Args:
            query: Search query
            
        Returns:
            Formatted search results
        """
        try:
            system_logger.info(f"Performing web search: {query}")
            
            if self.search_engine is None:
                return "Web search is currently unavailable. Please consult with your healthcare provider for the most current information."
            
            # Perform search
            if hasattr(self.search_engine, 'invoke'):
                results = self.search_engine.invoke({"query": query})
            else:
                results = self.search_engine.run(query)
            
            # Format results
            formatted_results = self._format_results(results, query)
            
            # Log search
            engine_name = "Tavily" if "Tavily" in str(type(self.search_engine)) else "DuckDuckGo"
            system_logger.log_web_search(
                query=query,
                search_engine=engine_name,
                num_results=len(results) if isinstance(results, list) else 1,
                success=True
            )
            
            return formatted_results
            
        except Exception as e:
            error_msg = f"Error performing web search: {str(e)}"
            system_logger.log_error("WebSearchError", error_msg, {"query": query})
            system_logger.log_web_search(
                query=query,
                search_engine="unknown",
                num_results=0,
                success=False
            )
            return "I encountered an error while searching the web. Please consult with your healthcare provider."
    
    def _format_results(self, results: Any, query: str) -> str:
        """
        Format search results.
        
        Args:
            results: Raw search results
            query: Original query
            
        Returns:
            Formatted results string
        """
        try:
            formatted = f"\n🔍 Web Search Results for: '{query}'\n"
            formatted += "=" * 60 + "\n\n"
            formatted += "⚠️ Note: This information comes from web search and should be verified with healthcare professionals.\n\n"
            
            if isinstance(results, str):
                # DuckDuckGo returns a string
                formatted += results
            elif isinstance(results, list):
                # Tavily returns a list of dictionaries
                for i, result in enumerate(results, 1):
                    if isinstance(result, dict):
                        title = result.get('title', result.get('name', 'No title'))
                        content = result.get('content', result.get('snippet', 'No content'))
                        url = result.get('url', result.get('link', ''))
                        
                        formatted += f"{i}. {title}\n"
                        formatted += f"   {content}\n"
                        if url:
                            formatted += f"   Source: {url}\n"
                        formatted += "\n"
            else:
                formatted += str(results)
            
            formatted += "\n" + "=" * 60 + "\n"
            formatted += "⚕️ Always consult with your healthcare provider before making any medical decisions.\n"
            
            return formatted
            
        except Exception as e:
            system_logger.error(f"Error formatting search results: {e}")
            return f"Found information about '{query}', but encountered formatting issues. Please consult your healthcare provider."
    
    def as_langchain_tool(self) -> Tool:
        """
        Convert to LangChain Tool.
        
        Returns:
            LangChain Tool instance
        """
        return Tool(
            name=self.name,
            description=self.description,
            func=self.search
        )


def create_web_search_tool() -> Tool:
    """
    Create and return a web search tool.
    
    Returns:
        LangChain Tool for web search
    """
    tool = WebSearchTool()
    return tool.as_langchain_tool()
