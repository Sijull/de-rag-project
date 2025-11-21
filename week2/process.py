import os
import weaviate
import weaviate.classes.config as wvc
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer

# Configuration
WEAVIATE_URL = "localhost"
WEAVIATE_PORT = 8090
WEAVIATE_GRPC_PORT = 50051
COLLECTION_NAME = "AirflowDocs"
DATA_DIR = "data"

# 1. Connect to Weaviate (v4 client)
client = weaviate.connect_to_local(
    host=WEAVIATE_URL,
    port=WEAVIATE_PORT,
    grpc_port=WEAVIATE_GRPC_PORT
)

def setup_collection():
    if client.collections.exists(COLLECTION_NAME):
        client.collections.delete(COLLECTION_NAME)
    
    # Create collection. 
    # CORRECTED: wvc.Configure (not wvc.config.Configure)
    client.collections.create(
        name=COLLECTION_NAME,
        vectorizer_config=wvc.Configure.Vectorizer.none(),
        properties=[
            wvc.Property(name="content", data_type=wvc.DataType.TEXT),
            wvc.Property(name="source", data_type=wvc.DataType.TEXT),
        ]
    )
    print(f"Collection {COLLECTION_NAME} created.")

def process_files():
    # Load Embedding Model (Runs on GPU if available)
    print("Loading embedding model...")
    model = SentenceTransformer('all-MiniLM-L6-v2') 

    # Text Splitter
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50
    )

    collection = client.collections.get(COLLECTION_NAME)
    
    # Iterate over files
    for filename in os.listdir(DATA_DIR):
        if filename.endswith(".txt"):
            file_path = os.path.join(DATA_DIR, filename)
            print(f"Processing {filename}...")
            
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()

            # Split text
            chunks = splitter.create_documents([text])
            
            # Prepare batch data
            print(f" - Found {len(chunks)} chunks. Embedding and inserting...")
            
            with collection.batch.dynamic() as batch:
                for chunk in chunks:
                    # Generate vector
                    vector = model.encode(chunk.page_content).tolist()
                    
                    # Add object to batch
                    batch.add_object(
                        properties={
                            "content": chunk.page_content,
                            "source": filename
                        },
                        vector=vector
                    )
            
            if len(collection.batch.failed_objects) > 0:
                print(f"Errors: {collection.batch.failed_objects}")
            else:
                print(" - Success!")

if __name__ == "__main__":
    try:
        setup_collection()
        process_files()
    finally:
        client.close()