"""
Comprehensive system tests for Post Discharge Medical AI Assistant.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from backend.database.database import get_db_manager
from backend.rag.vector_store import get_vector_store
from backend.tools.patient_retrieval import PatientRetrievalTool
from backend.tools.rag_tool import RAGTool


class TestDatabase:
    """Test database functionality."""
    
    def test_database_initialization(self):
        """Test database can be initialized."""
        db_manager = get_db_manager()
        assert db_manager is not None
    
    def test_patient_retrieval(self):
        """Test patient retrieval by name."""
        db_manager = get_db_manager()
        patient = db_manager.get_patient_by_name("John Smith")
        
        assert patient is not None
        assert patient['patient_name'] == "John Smith"
        assert patient['primary_diagnosis'] == "Chronic Kidney Disease Stage 3"
        assert len(patient['medications']) > 0
    
    def test_patient_search(self):
        """Test patient search functionality."""
        db_manager = get_db_manager()
        results = db_manager.search_patients("kidney")
        
        assert len(results) > 0
        assert any("kidney" in p['primary_diagnosis'].lower() for p in results)
    
    def test_all_patients(self):
        """Test retrieving all patients."""
        db_manager = get_db_manager()
        patients = db_manager.get_all_patients()
        
        assert len(patients) >= 27
        assert all('patient_name' in p for p in patients)


class TestVectorStore:
    """Test vector store functionality."""
    
    def test_vector_store_initialization(self):
        """Test vector store can be initialized."""
        vector_store = get_vector_store()
        assert vector_store is not None
    
    def test_vector_store_stats(self):
        """Test vector store statistics."""
        vector_store = get_vector_store()
        stats = vector_store.get_collection_stats()
        
        assert stats['status'] in ['initialized', 'not_initialized']
        assert 'count' in stats
    
    def test_similarity_search(self):
        """Test similarity search functionality."""
        vector_store = get_vector_store()
        results = vector_store.similarity_search(
            "What is chronic kidney disease?",
            k=3
        )
        
        # If vector store is initialized, should return results
        if vector_store.get_collection_stats()['count'] > 0:
            assert len(results) > 0
            assert all('content' in r for r in results)


class TestTools:
    """Test agent tools."""
    
    def test_patient_retrieval_tool(self):
        """Test patient retrieval tool."""
        tool = PatientRetrievalTool()
        result = tool.retrieve_patient("John Smith")
        
        assert "John Smith" in result
        assert "Chronic Kidney Disease" in result
    
    def test_patient_not_found(self):
        """Test patient retrieval with non-existent patient."""
        tool = PatientRetrievalTool()
        result = tool.retrieve_patient("Nonexistent Patient")
        
        assert "couldn't find" in result.lower() or "not found" in result.lower()
    
    def test_rag_tool(self):
        """Test RAG tool."""
        tool = RAGTool()
        
        # Test if vector store is initialized
        vector_store = get_vector_store()
        stats = vector_store.get_collection_stats()
        
        if stats['count'] > 0:
            result = tool.retrieve("What is chronic kidney disease?")
            assert len(result) > 0


def run_tests():
    """Run all tests and print results."""
    print("=" * 60)
    print("Running System Tests")
    print("=" * 60)
    print()
    
    # Test Database
    print("Testing Database...")
    try:
        test_db = TestDatabase()
        test_db.test_database_initialization()
        print("✅ Database initialization")
        
        test_db.test_patient_retrieval()
        print("✅ Patient retrieval")
        
        test_db.test_patient_search()
        print("✅ Patient search")
        
        test_db.test_all_patients()
        print("✅ All patients retrieval")
    except Exception as e:
        print(f"❌ Database tests failed: {e}")
    
    print()
    
    # Test Vector Store
    print("Testing Vector Store...")
    try:
        test_vs = TestVectorStore()
        test_vs.test_vector_store_initialization()
        print("✅ Vector store initialization")
        
        test_vs.test_vector_store_stats()
        print("✅ Vector store statistics")
        
        test_vs.test_similarity_search()
        print("✅ Similarity search")
    except Exception as e:
        print(f"❌ Vector store tests failed: {e}")
    
    print()
    
    # Test Tools
    print("Testing Tools...")
    try:
        test_tools = TestTools()
        test_tools.test_patient_retrieval_tool()
        print("✅ Patient retrieval tool")
        
        test_tools.test_patient_not_found()
        print("✅ Patient not found handling")
        
        test_tools.test_rag_tool()
        print("✅ RAG tool")
    except Exception as e:
        print(f"❌ Tools tests failed: {e}")
    
    print()
    print("=" * 60)
    print("Tests Complete!")
    print("=" * 60)


if __name__ == "__main__":
    run_tests()
