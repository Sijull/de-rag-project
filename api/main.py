from fastapi import FastAPI
import os
import requests

app = FastAPI()

# Read config from environment variables
OLLAMA_HOST_URL = os.getenv("OLLAMA_HOST_URL")
VECTOR_DB_URL = os.getenv("VECTOR_DB_URL")

@app.get("/")
def read_root():
    """Test endpoint to see if the API is running."""
    return {
        "message": "RAG API is running!",
        "ollama_host": OLLAMA_HOST_URL,
        "vector_db_host": VECTOR_DB_URL
    }

@app.post("/chat")
def chat_stub(query: dict):
    """
    A stub for the chat endpoint. For Weekend 1, we just return a
    fake response. This proves the UI can call the API.
    """
    user_query = query.get("message", "No query provided")
    
    # In Weekend 4, you'll add the real RAG logic here.
    # For now, just show we received the query.
    return {
        "response": f"You asked: '{user_query}'. The real RAG logic is not built yet!"
    }

@app.get("/test-ollama")
def test_ollama():
    """A test endpoint to see if the API can reach the host Ollama."""
    try:
        # OLLAMA_HOST_URL is http://host.docker.internal:11434
        response = requests.get(f"{OLLAMA_HOST_URL}/api/tags")
        response.raise_for_status() # Raise an exception for bad status codes
        return {"status": "SUCCESS", "response": response.json()}
    except Exception as e:
        return {"status": "FAILED", "error": str(e)}