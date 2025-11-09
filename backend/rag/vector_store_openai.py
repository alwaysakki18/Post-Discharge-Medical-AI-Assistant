"""
Vector store implementation using OpenAI embeddings (more reliable than local models).
"""

import chromadb
from chromadb.config import Settings
from typing import List, Dict, Any, Optional
from pathlib import Path
import hashlib
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.docstore.document import Document
from langchain_community.document_loaders import PyPDFLoader

from ..utils.logger import system_logger
from ..config import settings


class VectorStoreManager:
    """
    Manages vector store for RAG implementation using OpenAI embeddings.
    """
    
    def __init__(
        self,
        persist_directory: str = "./data/vector_db",
        collection_name: str = "nephrology_docs"
    ):
        """Initialize vector store manager with OpenAI embeddings."""
        self.persist_directory = Path(persist_directory)
        self.persist_directory.mkdir(parents=True, exist_ok=True)
        self.collection_name = collection_name
        
        # Initialize OpenAI embeddings (more reliable)
        system_logger.info("Initializing OpenAI embeddings...")
        self.embeddings = OpenAIEmbeddings(
            model="text-embedding-3-small"  # Latest, efficient model
        )
        
        # Initialize text splitter
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.chunk_size,
            chunk_overlap=settings.chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
        
        # Initialize or load vector store
        self.vector_store = None
        self._initialize_vector_store()
        
        system_logger.info(f"Vector store initialized: {persist_directory}")
    
    def _initialize_vector_store(self):
        """Initialize or load existing vector store."""
        try:
            self.vector_store = Chroma(
                collection_name=self.collection_name,
                embedding_function=self.embeddings,
                persist_directory=str(self.persist_directory)
            )
            
            collection = self.vector_store._collection
            count = collection.count()
            
            if count > 0:
                system_logger.info(f"Loaded existing vector store with {count} documents")
            else:
                system_logger.info("Vector store is empty, ready for indexing")
                
        except Exception as e:
            system_logger.warning(f"Could not load existing vector store: {e}")
            self.vector_store = None
    
    def index_document(self, file_path: str, metadata: Optional[Dict[str, Any]] = None):
        """Index a document (PDF or TXT) into the vector store."""
        try:
            file_path_obj = Path(file_path)
            file_extension = file_path_obj.suffix.lower()
            
            # Load document based on file type
            if file_extension == '.pdf':
                system_logger.info(f"Loading PDF document: {file_path}")
                loader = PyPDFLoader(file_path)
                pages = loader.load()
                text = "\n\n".join([page.page_content for page in pages])
                system_logger.info(f"Loaded PDF with {len(pages)} pages")
                
            elif file_extension == '.txt':
                system_logger.info(f"Loading text document: {file_path}")
                with open(file_path, 'r', encoding='utf-8') as f:
                    text = f.read()
            else:
                raise ValueError(f"Unsupported file type: {file_extension}")
            
            doc_hash = hashlib.md5(text.encode()).hexdigest()
            chunks = self.text_splitter.split_text(text)
            system_logger.info(f"Split document into {len(chunks)} chunks")
            
            # Create documents with metadata
            documents = []
            for i, chunk in enumerate(chunks):
                doc_metadata = {
                    "source": file_path,
                    "chunk_id": i,
                    "doc_hash": doc_hash,
                    "file_type": file_extension,
                    **(metadata or {})
                }
                documents.append(Document(page_content=chunk, metadata=doc_metadata))
            
            # Create or update vector store
            if self.vector_store is None:
                self.vector_store = Chroma.from_documents(
                    documents=documents,
                    embedding=self.embeddings,
                    collection_name=self.collection_name,
                    persist_directory=str(self.persist_directory)
                )
            else:
                self.vector_store.add_documents(documents)
            
            self.vector_store.persist()
            system_logger.info(f"Indexed {len(documents)} chunks from {file_path}")
            
        except Exception as e:
            system_logger.log_error("VectorStoreError", f"Error indexing document: {str(e)}")
            raise
    
    def similarity_search(
        self,
        query: str,
        k: int = 5,
        filter_dict: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Perform similarity search."""
        if self.vector_store is None:
            system_logger.warning("Vector store not initialized")
            return []
        
        try:
            results = self.vector_store.similarity_search_with_score(
                query=query,
                k=k,
                filter=filter_dict
            )
            
            formatted_results = []
            for doc, score in results:
                formatted_results.append({
                    "content": doc.page_content,
                    "metadata": doc.metadata,
                    "score": float(score)
                })
            
            sources = [r["metadata"].get("source", "unknown") for r in formatted_results]
            system_logger.log_rag_retrieval(
                query=query,
                num_results=len(formatted_results),
                sources=list(set(sources)),
                success=True
            )
            
            return formatted_results
            
        except Exception as e:
            system_logger.log_error("VectorStoreError", f"Error in similarity search: {str(e)}")
            system_logger.log_rag_retrieval(
                query=query,
                num_results=0,
                sources=[],
                success=False
            )
            return []
    
    def get_retriever(self, k: int = 5):
        """Get a LangChain retriever."""
        if self.vector_store is None:
            raise ValueError("Vector store not initialized")
        
        return self.vector_store.as_retriever(
            search_type="similarity",
            search_kwargs={"k": k}
        )
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about the collection."""
        if self.vector_store is None:
            return {"count": 0, "status": "not_initialized"}
        
        try:
            collection = self.vector_store._collection
            count = collection.count()
            
            return {
                "count": count,
                "collection_name": self.collection_name,
                "persist_directory": str(self.persist_directory),
                "status": "initialized"
            }
        except Exception as e:
            system_logger.log_error("VectorStoreError", f"Error getting stats: {str(e)}")
            return {"count": 0, "status": "error", "error": str(e)}


# Global vector store instance
vector_store_manager = None

def get_vector_store() -> VectorStoreManager:
    """Get or create vector store manager instance."""
    global vector_store_manager
    if vector_store_manager is None:
        vector_store_manager = VectorStoreManager(
            persist_directory=settings.vector_db_path
        )
    return vector_store_manager
