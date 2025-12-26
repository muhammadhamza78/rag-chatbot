from qdrant_client import QdrantClient
from dotenv import load_dotenv
import os
import cohere

load_dotenv()

# Initialize clients
qdrant_client = QdrantClient(
    url=os.getenv('QDRANT_URL'),
    api_key=os.getenv('QDRANT_API_KEY')
)

cohere_client = cohere.Client(os.getenv('COHERE_API_KEY'))

COLLECTION_NAME = os.getenv('QDRANT_COLLECTION_NAME', 'my-embedded')

def retrieve_documents(query, top_k=5):
    """Query se relevant documents retrieve karo"""
    
    # Query ko embed karo
    response = cohere_client.embed(
        texts=[query],
        model=os.getenv('EMBEDDING_MODEL', 'embed-english-v3.0'),
        input_type='search_query'
    )
    
    query_embedding = response.embeddings[0]
    
    # Qdrant se search karo (FIXED METHOD)
    search_results = qdrant_client.query_points(
        collection_name=COLLECTION_NAME,
        query=query_embedding,
        limit=top_k
    ).points
    
    return search_results

if __name__ == "__main__":
    query = input("Enter your query: ")
    
    try:
        results = retrieve_documents(query)
        
        print(f"\n{'='*50}")
        print(f"Found {len(results)} results")
        print(f"{'='*50}\n")
        
        for i, result in enumerate(results, 1):
            print(f"{i}. Score: {result.score:.4f}")
            print(f"   Text: {result.payload.get('text', 'N/A')[:200]}...")
            print()
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nMake sure:")
        print("1. Collection exists and has data")
        print("2. Run 'python upload_data.py' first")
