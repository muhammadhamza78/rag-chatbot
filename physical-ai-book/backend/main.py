from flask import Flask, request, jsonify
from flask_cors import CORS
from qdrant_client import QdrantClient
from dotenv import load_dotenv
import os
import cohere
from groq import Groq

# Load environment variables
load_dotenv(dotenv_path='../.env')

app = Flask(__name__)
CORS(app)

# Initialize clients
qdrant_client = QdrantClient(
    url=os.getenv('QDRANT_URL'),
    api_key=os.getenv('QDRANT_API_KEY')
)

cohere_client = cohere.Client(os.getenv('COHERE_API_KEY'))
groq_client = Groq(api_key=os.getenv('GROQ_API_KEY', 'gsk_free'))  # Free tier

COLLECTION_NAME = os.getenv('QDRANT_COLLECTION_NAME', 'my-embedded')

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok', 'message': 'Backend is running!'})

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        query = data.get('query', '')
        
        if not query:
            return jsonify({'error': 'Query is required'}), 400
        
        print(f"Received query: {query}")
        
        # Step 1: Embed query
        embed_response = cohere_client.embed(
            texts=[query],
            model=os.getenv('EMBEDDING_MODEL', 'embed-english-v3.0'),
            input_type='search_query'
        )
        
        query_embedding = embed_response.embeddings[0]
        
        # Step 2: Search in Qdrant
        search_results = qdrant_client.query_points(
            collection_name=COLLECTION_NAME,
            query=query_embedding,
            limit=3
        ).points
        
        print(f"Found {len(search_results)} documents")
        
        if not search_results:
            return jsonify({
                'answer': "I don't have enough information to answer that question."
            })
        
        # Step 3: Prepare context
        context = "\n\n".join([
            doc.payload.get('text', '') for doc in search_results
        ])
        
        # Step 4: Generate answer with Groq (FREE & FAST)
        completion = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",  # Free model
            messages=[
                {
                    "role": "system",
                    "content": "Answer concisely based on context."
                },
                {
                    "role": "user",
                    "content": f"Context:\n{context}\n\nQuestion: {query}"
                }
            ],
            temperature=0.7,
            max_tokens=300
        )
        
        answer = completion.choices[0].message.content
        
        return jsonify({'answer': answer})
    
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("Starting Flask backend...")
    app.run(debug=True, port=5000, host='0.0.0.0')