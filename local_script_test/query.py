import weaviate
import requests
import json
from sentence_transformers import SentenceTransformer

# Configuration
WEAVIATE_URL = "localhost"
WEAVIATE_PORT = 8090
WEAVIATE_GRPC_PORT = 50051
COLLECTION_NAME = "AirflowDocs"
OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "phi3:mini" # Make sure you have run `ollama pull phi3:mini`

def chat():
    # 1. Connect to Weaviate and Load Model
    client = weaviate.connect_to_local(
        host=WEAVIATE_URL,
        port=WEAVIATE_PORT,
        grpc_port=WEAVIATE_GRPC_PORT
    )
    print("Loading embedding model...")
    model = SentenceTransformer('all-MiniLM-L6-v2')
    collection = client.collections.get(COLLECTION_NAME)

    print("\n--- RAG System Ready (Type 'exit' to quit) ---")
    
    while True:
        query_text = input("\nUser: ")
        if query_text.lower() == 'exit':
            break

        # 2. Vector Search
        query_vector = model.encode(query_text).tolist()
        
        response = collection.query.near_vector(
            near_vector=query_vector,
            limit=3 # Retrieve top 3 chunks
        )

        # 3. Construct Context
        context_text = ""
        for obj in response.objects:
            context_text += f"{obj.properties['content']}\n---\n"

        # 4. Generate Prompt
        prompt = f"""
        You are a helpful assistant. Answer the question using only the following context.
        
        Context:
        {context_text}
        
        Question: {query_text}
        
        Answer:
        """

        # 5. Call Ollama
        payload = {
            "model": OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False
        }

        try:
            print("Thinking...")
            resp = requests.post(OLLAMA_URL, json=payload)
            resp_json = resp.json()
            print(f"\nAI: {resp_json['response']}")
        except Exception as e:
            print(f"Error communicating with Ollama: {e}")

    client.close()

if __name__ == "__main__":
    chat()