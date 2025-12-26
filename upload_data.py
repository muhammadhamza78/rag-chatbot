from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from dotenv import load_dotenv
import os
import cohere

load_dotenv()

qdrant_client = QdrantClient(
    url=os.getenv('QDRANT_URL'),
    api_key=os.getenv('QDRANT_API_KEY')
)

cohere_client = cohere.Client(os.getenv('COHERE_API_KEY'))

COLLECTION_NAME = os.getenv('QDRANT_COLLECTION_NAME', 'my-embedded')

# Sample documents about ROS 2
documents = [
    "ROS 2 (Robot Operating System 2) is a flexible framework for writing robot software with improved security and real-time capabilities.",
    "ROS 2 uses DDS (Data Distribution Service) for communication, making it more suitable for production environments.",
    "ROS 2 supports multiple programming languages including Python, C++, and has better support for embedded systems.",
    "Unlike ROS 1, ROS 2 is designed for multi-robot systems and works on various platforms including Windows, macOS, and Linux.",
    "ROS 2 provides quality of service (QoS) settings for network communication, allowing developers to tune reliability and performance.",
    "Machine Learning is a subset of AI that enables systems to learn from data.",
    "Deep Learning uses neural networks with multiple layers to solve complex problems.",
    "Natural Language Processing helps computers understand and generate human language.",
    "Computer Vision allows machines to interpret and understand visual information from the world."
]

print("Embedding documents to get dimension size...")
response = cohere_client.embed(
    texts=documents[:1],  # Test with 1 document
    model=os.getenv('EMBEDDING_MODEL', 'embed-english-v3.0'),
    input_type='search_document'
)

embedding_dim = len(response.embeddings[0])
print(f"Detected embedding dimension: {embedding_dim}")

print(f"Creating collection with {embedding_dim} dimensions...")
try:
    qdrant_client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(size=embedding_dim, distance=Distance.COSINE)
    )
    print("✓ Collection created!")
except Exception as e:
    print(f"Note: {e}")

print("Embedding all documents...")
response = cohere_client.embed(
    texts=documents,
    model=os.getenv('EMBEDDING_MODEL', 'embed-english-v3.0'),
    input_type='search_document'
)

print("Uploading to Qdrant...")
points = [
    PointStruct(
        id=i,
        vector=embedding,
        payload={'text': doc}
    )
    for i, (embedding, doc) in enumerate(zip(response.embeddings, documents))
]

qdrant_client.upsert(collection_name=COLLECTION_NAME, points=points)
print(f"✓ Successfully uploaded {len(documents)} documents!")

# Verify
info = qdrant_client.get_collection(COLLECTION_NAME)
print(f"✓ Collection now has {info.points_count} points with {embedding_dim} dimensions")
