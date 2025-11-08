"""
Vector store implementation for RAG using ChromaDB.
"""

import chromadb
from chromadb.config import Settings
from typing import List, Dict, Any, Optional
from pathlib import Path
import hashlib

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.docstore.document import Document
from langchain_community.document_loaders import PyPDFLoader

from ..utils.logger import system_logger
from ..config import settings


class VectorStoreManager:
    """
    Manages vector store for RAG implementation.
    Handles document chunking, embedding, and retrieval.
    """
    
    def __init__(
        self,
        persist_directory: str = "./data/vector_db",
        collection_name: str = "nephrology_docs"
    ):
        """
        Initialize vector store manager.
        
        Args:
            persist_directory: Directory to persist vector database
            collection_name: Name of the collection
        """
        self.persist_directory = Path(persist_directory)
        self.persist_directory.mkdir(parents=True, exist_ok=True)
        self.collection_name = collection_name
        
        # Initialize embeddings
        system_logger.info("Initializing embeddings model...")
        self.embeddings = HuggingFaceEmbeddings(
            model_name=settings.embedding_model,
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
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
            # Try to load existing vector store
            self.vector_store = Chroma(
                collection_name=self.collection_name,
                embedding_function=self.embeddings,
                persist_directory=str(self.persist_directory)
            )
            
            # Check if collection has documents
            collection = self.vector_store._collection
            count = collection.count()
            
            if count > 0:
                system_logger.info(f"Loaded existing vector store with {count} documents")
            else:
                system_logger.info("Vector store is empty, ready for indexing")
                
        except Exception as e:
            system_logger.warning(f"Could not load existing vector store: {e}")
            system_logger.info("Creating new vector store")
            self.vector_store = None
    
    def index_document(self, file_path: str, metadata: Optional[Dict[str, Any]] = None):
        """
        Index a document into the vector store.
        Supports both text files (.txt) and PDF files (.pdf).
        
        Args:
            file_path: Path to the document file
            metadata: Additional metadata for the document
        """
        try:
            file_path_obj = Path(file_path)
            file_extension = file_path_obj.suffix.lower()
            
            # Load document based on file type
            if file_extension == '.pdf':
                system_logger.info(f"Loading PDF document: {file_path}")
                loader = PyPDFLoader(file_path)
                pages = loader.load()
                
                # Extract text from all pages
                text = "\n\n".join([page.page_content for page in pages])
                system_logger.info(f"Loaded PDF with {len(pages)} pages")
                
            elif file_extension == '.txt':
                system_logger.info(f"Loading text document: {file_path}")
                with open(file_path, 'r', encoding='utf-8') as f:
                    text = f.read()
            else:
                raise ValueError(f"Unsupported file type: {file_extension}. Supported types: .pdf, .txt")
            
            # Create document hash for deduplication
            doc_hash = hashlib.md5(text.encode()).hexdigest()
            
            # Split into chunks
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
            
            # Persist
            self.vector_store.persist()
            
            system_logger.info(f"Indexed {len(documents)} chunks from {file_path}")
            
        except Exception as e:
            system_logger.log_error("VectorStoreError", f"Error indexing document: {str(e)}")
            raise
    
    def index_documents(self, file_paths: List[str]):
        """
        Index multiple documents.
        
        Args:
            file_paths: List of file paths to index
        """
        for file_path in file_paths:
            try:
                self.index_document(file_path)
            except Exception as e:
                system_logger.error(f"Failed to index {file_path}: {e}")
    
    def similarity_search(
        self,
        query: str,
        k: int = 5,
        filter_dict: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Perform similarity search.
        
        Args:
            query: Search query
            k: Number of results to return
            filter_dict: Optional metadata filter
            
        Returns:
            List of relevant documents with metadata
        """
        if self.vector_store is None:
            system_logger.warning("Vector store not initialized")
            return []
        
        try:
            # Perform search
            results = self.vector_store.similarity_search_with_score(
                query=query,
                k=k,
                filter=filter_dict
            )
            
            # Format results
            formatted_results = []
            for doc, score in results:
                formatted_results.append({
                    "content": doc.page_content,
                    "metadata": doc.metadata,
                    "score": float(score)
                })
            
            # Log retrieval
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
        """
        Get a LangChain retriever.
        
        Args:
            k: Number of documents to retrieve
            
        Returns:
            LangChain retriever
        """
        if self.vector_store is None:
            raise ValueError("Vector store not initialized")
        
        return self.vector_store.as_retriever(
            search_type="similarity",
            search_kwargs={"k": k}
        )
    
    def delete_collection(self):
        """Delete the entire collection."""
        try:
            if self.vector_store is not None:
                self.vector_store.delete_collection()
                system_logger.info(f"Deleted collection: {self.collection_name}")
        except Exception as e:
            system_logger.log_error("VectorStoreError", f"Error deleting collection: {str(e)}")
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the collection.
        
        Returns:
            Dictionary with collection statistics
        """
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
