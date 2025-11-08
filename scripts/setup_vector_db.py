"""
Script to initialize and populate the vector database.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.rag.vector_store import get_vector_store
from backend.utils.logger import system_logger


def main():
    """Initialize vector database and index reference materials."""
    try:
        print("=" * 60)
        print("Post Discharge Medical AI Assistant - Vector DB Setup")
        print("=" * 60)
        print()
        
        # Initialize vector store
        print("🔍 Initializing vector store...")
        vector_store = get_vector_store()
        print("✅ Vector store initialized")
        print()
        
        # Check if already indexed
        stats = vector_store.get_collection_stats()
        if stats.get("count", 0) > 0:
            print(f"ℹ️  Vector store already contains {stats['count']} documents")
            response = input("Do you want to re-index? (yes/no): ")
            if response.lower() != "yes":
                print("Skipping indexing.")
                return
            
            print("🗑️  Deleting existing collection...")
            vector_store.delete_collection()
            vector_store = get_vector_store()
        
        # Index nephrology reference - Try PDF first, then fallback to TXT
        print("📚 Indexing nephrology reference materials...")
        
        # Check for PDF file first (comprehensive clinical nephrology)
        pdf_file = Path(__file__).parent.parent / "knowledge base for RAG" / "comprehensive-clinical-nephrology.pdf"
        txt_file = Path(__file__).parent.parent / "data" / "nephrology_reference.txt"
        
        if pdf_file.exists():
            print(f"📄 Found PDF reference: {pdf_file.name}")
            print("   This may take several minutes to process...")
            vector_store.index_document(
                str(pdf_file),
                metadata={
                    "type": "reference",
                    "subject": "nephrology",
                    "source": "comprehensive-clinical-nephrology.pdf",
                    "format": "pdf"
                }
            )
            print("✅ PDF reference materials indexed")
        elif txt_file.exists():
            print(f"📄 Found text reference: {txt_file.name}")
            vector_store.index_document(
                str(txt_file),
                metadata={
                    "type": "reference",
                    "subject": "nephrology",
                    "source": "nephrology_reference.txt",
                    "format": "txt"
                }
            )
            print("✅ Text reference materials indexed")
        else:
            print(f"❌ Error: No reference file found")
            print(f"   Looked for:")
            print(f"   - {pdf_file}")
            print(f"   - {txt_file}")
            return
        
        print()
        
        # Verify indexing
        stats = vector_store.get_collection_stats()
        print(f"📈 Vector Store Statistics:")
        print(f"   - Total documents: {stats.get('count', 0)}")
        print(f"   - Collection: {stats.get('collection_name', 'Unknown')}")
        print(f"   - Status: {stats.get('status', 'Unknown')}")
        print()
        
        # Test search
        print("🧪 Testing search functionality...")
        test_query = "What is chronic kidney disease?"
        results = vector_store.similarity_search(test_query, k=3)
        
        if results:
            print(f"✅ Search test successful! Found {len(results)} relevant chunks")
            print(f"   Query: '{test_query}'")
            print(f"   Top result preview: {results[0]['content'][:100]}...")
        else:
            print("⚠️  Search test returned no results")
        
        print()
        print("=" * 60)
        print("✅ Vector database setup complete!")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ Error during vector database setup: {str(e)}")
        system_logger.log_error("VectorDBSetupError", str(e))
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
