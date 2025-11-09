"""
Script to initialize vector database using OpenAI embeddings.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.rag.vector_store_openai import get_vector_store
from backend.utils.logger import system_logger


def main():
    """Initialize vector database with OpenAI embeddings."""
    try:
        print("=" * 60)
        print("Vector DB Setup - Using OpenAI Embeddings")
        print("=" * 60)
        print()
        
        # Initialize vector store
        print("🔍 Initializing vector store with OpenAI embeddings...")
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
        
        # Index nephrology reference (using text file for speed)
        print("📚 Indexing nephrology reference materials...")
        txt_file = Path(__file__).parent.parent / "data" / "nephrology_reference.txt"
        
        if not txt_file.exists():
            print(f"❌ Error: Reference file not found: {txt_file}")
            return
        
        print(f"📄 Found text reference: {txt_file.name}")
        print("   Processing with OpenAI embeddings...")
        
        vector_store.index_document(
            str(txt_file),
            metadata={
                "type": "reference",
                "subject": "nephrology",
                "source": "nephrology_reference.txt",
                "format": "txt"
            }
        )
        print("✅ Reference materials indexed")
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
