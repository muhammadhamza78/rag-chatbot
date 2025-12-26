from qdrant_client import QdrantClient
from dotenv import load_dotenv
import os
import cohere
from openai import OpenAI

load_dotenv()

# Initialize clients
qdrant_client = QdrantClient(
    url=os.getenv('QDRANT_URL'),
    api_key=os.getenv('QDRANT_API_KEY')
)

cohere_client = cohere.Client(os.getenv('COHERE_API_KEY'))
openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

COLLECTION_NAME = os.getenv('QDRANT_COLLECTION_NAME', 'my-embedded')

def retrieve_documents(query, top_k=3):
    """Query se relevant documents retrieve karo"""
    response = cohere_client.embed(
        texts=[query],
        model=os.getenv('EMBEDDING_MODEL', 'embed-english-v3.0'),
        input_type='search_query'
    )
    
    query_embedding = response.embeddings[0]
    
    search_results = qdrant_client.query_points(
        collection_name=COLLECTION_NAME,
        query=query_embedding,
        limit=top_k
    ).points
    
    return search_results

def generate_answer(query, context_docs):
    """Retrieved documents se answer generate karo using OpenAI"""
    context = "\n\n".join([doc.payload.get('text', '') for doc in context_docs])
    
    response = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful assistant. Answer questions based on the provided context concisely."},
            {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {query}"}
        ],
        temperature=0.7,
        max_tokens=300
    )
    
    return response.choices[0].message.content

def rag_agent(query):
    """RAG pipeline: Retrieve + Generate"""
    print(f"\n🔍 Searching for: {query}")
    print("=" * 60)
    
    # Step 1: Retrieve
    docs = retrieve_documents(query, top_k=3)
    print(f"\n📚 Found {len(docs)} relevant documents:")
    for i, doc in enumerate(docs, 1):
        print(f"\n{i}. [Score: {doc.score:.4f}]")
        print(f"   {doc.payload.get('text', 'N/A')[:150]}...")
    
    # Step 2: Generate
    print(f"\n💡 Generating answer...")
    print("=" * 60)
    answer = generate_answer(query, docs)
    print(f"\n{answer}\n")
    
    return answer

if __name__ == "__main__":
    print("🤖 RAG Agent - Ask me anything!")
    print("Type 'exit' to quit\n")
    
    while True:
        query = input("You: ").strip()
        
        if query.lower() in ['exit', 'quit', 'bye']:
            print("👋 Goodbye!")
            break
            
        if not query:
            continue
            
        try:
            rag_agent(query)
        except Exception as e:
            print(f"\n❌ Error: {e}\n")
