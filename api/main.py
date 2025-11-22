from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
import requests
import weaviate
from sentence_transformers import SentenceTransformer

app = FastAPI()

# --- Configuration ---
# Get these from docker-compose environment variables
OLLAMA_HOST = os.getenv("OLLAMA_HOST_URL", "http://host.docker.internal:11434")
WEAVIATE_HOST = os.getenv("WEAVIATE_HOST", "weaviate")
WEAVIATE_PORT = int(os.getenv("WEAVIATE_PORT", 8080))
WEAVIATE_GRPC_PORT = int(os.getenv("WEAVIATE_GRPC_PORT", 50051))
OLLAMA_MODEL = "phi3:mini"  # or "llama3.2"

# --- Global State ---
# We load the model once at startup to save time on each request
print("Loading embedding model...")
embedding_model = SentenceTransformer('all-MiniLM-L6-v2', device='cpu')
print("Model loaded.")

class ChatRequest(BaseModel):
    message: str

@app.get("/")
def read_root():
    return {"status": "RAG API is ready", "config": {"ollama": OLLAMA_HOST, "weaviate": WEAVIATE_HOST}}

@app.post("/chat")
def chat_endpoint(request: ChatRequest):
    user_query = request.message
    
    # 1. Connect to Weaviate
    client = weaviate.connect_to_local(
        host=WEAVIATE_HOST,
        port=WEAVIATE_PORT,
        grpc_port=WEAVIATE_GRPC_PORT
    )
    
    try:
        collection = client.collections.get("AirflowDocs")
        
        # 2. Generate Embedding for the User's Question
        query_vector = embedding_model.encode(user_query).tolist()
        
        # 3. Search Weaviate (Semantic Search)
        search_results = collection.query.near_vector(
            near_vector=query_vector,
            limit=3, # Get top 3 most relevant chunks
            return_metadata=["distance"]
        )
        
        # 4. Build Context String & Collect Sources
        context_text = ""
        sources = []
        
        for obj in search_results.objects:
            content = obj.properties.get("content", "")
            source = obj.properties.get("source", "unknown")
            
            context_text += f"{content}\n---\n"
            sources.append(source)
            
        # 5. Construct the Prompt for Ollama
        prompt = f"""
        You are a helpful assistant. Answer the question based ONLY on the following context.
        
        Context:
        {context_text}
        
        Question: {user_query}
        
        Answer:
        """
        
        # 6. Call Ollama API
        payload = {
            "model": OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False
        }
        
        print(f"Sending request to Ollama at {OLLAMA_HOST}...")
        response = requests.post(f"{OLLAMA_HOST}/api/generate", json=payload)
        
        if response.status_code == 200:
            ai_response = response.json().get("response", "")
            return {
                "response": ai_response,
                "sources": list(set(sources)) # Unique sources
            }
        else:
            raise HTTPException(status_code=500, detail=f"Ollama Error: {response.text}")

    except Exception as e:
        print(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        client.close()




# from fastapi import FastAPI
# import os
# import requests

# app = FastAPI()

# # Read config from environment variables
# OLLAMA_HOST_URL = os.getenv("OLLAMA_HOST_URL")
# VECTOR_DB_URL = os.getenv("VECTOR_DB_URL")

# @app.get("/")
# def read_root():
#     """Test endpoint to see if the API is running."""
#     return {
#         "message": "RAG API is running!",
#         "ollama_host": OLLAMA_HOST_URL,
#         "vector_db_host": VECTOR_DB_URL
#     }

# @app.post("/chat")
# def chat_stub(query: dict):
#     """
#     A stub for the chat endpoint. For Weekend 1, we just return a
#     fake response. This proves the UI can call the API.
#     """
#     user_query = query.get("message", "No query provided")
    
#     # In Weekend 4, you'll add the real RAG logic here.
#     # For now, just show we received the query.
#     return {
#         "response": f"You asked: '{user_query}'. The real RAG logic is not built yet!"
#     }

# @app.get("/test-ollama")
# def test_ollama():
#     """A test endpoint to see if the API can reach the host Ollama."""
#     try:
#         # OLLAMA_HOST_URL is http://host.docker.internal:11434
#         response = requests.get(f"{OLLAMA_HOST_URL}/api/tags")
#         response.raise_for_status() # Raise an exception for bad status codes
#         return {"status": "SUCCESS", "response": response.json()}
#     except Exception as e:
#         return {"status": "FAILED", "error": str(e)}