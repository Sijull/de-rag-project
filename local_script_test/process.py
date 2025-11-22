import weaviate
import weaviate.classes.config as wvc
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer
from minio import Minio
import io

# --- Configuration ---
# Weaviate Settings
WEAVIATE_URL = "localhost"
WEAVIATE_PORT = 8090
WEAVIATE_GRPC_PORT = 50051
COLLECTION_NAME = "AirflowDocs"

# MinIO Settings
MINIO_CLIENT = Minio(
    "localhost:9000",
    access_key="minioadmin",
    secret_key="minioadmin",
    secure=False
)
BUCKET_NAME = "rag-raw-data"

# Connect to Weaviate
client = weaviate.connect_to_local(
    host=WEAVIATE_URL,
    port=WEAVIATE_PORT,
    grpc_port=WEAVIATE_GRPC_PORT
)

def setup_collection():
    if client.collections.exists(COLLECTION_NAME):
        client.collections.delete(COLLECTION_NAME)
    
    client.collections.create(
        name=COLLECTION_NAME,
        vectorizer_config=wvc.Configure.Vectorizer.none(),
        properties=[
            wvc.Property(name="content", data_type=wvc.DataType.TEXT),
            wvc.Property(name="source", data_type=wvc.DataType.TEXT),
        ]
    )
    print(f"Collection {COLLECTION_NAME} created.")

def process_minio_files():
    print("Loading embedding model...")
    model = SentenceTransformer('all-MiniLM-L6-v2') 
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    collection = client.collections.get(COLLECTION_NAME)
    
    # 1. List objects in MinIO bucket
    if not MINIO_CLIENT.bucket_exists(BUCKET_NAME):
        print(f"Bucket {BUCKET_NAME} does not exist!")
        return

    objects = MINIO_CLIENT.list_objects(BUCKET_NAME)
    
    for obj in objects:
        filename = obj.object_name
        if not filename.endswith(".txt"):
            continue
            
        print(f"Processing {filename} from MinIO...")
        
        # 2. Get object content
        try:
            response = MINIO_CLIENT.get_object(BUCKET_NAME, filename)
            text = response.read().decode('utf-8')
        finally:
            response.close()
            
        # 3. Split and Vectorize
        chunks = splitter.create_documents([text])
        print(f" - Generated {len(chunks)} chunks.")
        
        with collection.batch.dynamic() as batch:
            for chunk in chunks:
                vector = model.encode(chunk.page_content).tolist()
                batch.add_object(
                    properties={
                        "content": chunk.page_content,
                        "source": f"minio://{BUCKET_NAME}/{filename}"
                    },
                    vector=vector
                )
        
        if len(collection.batch.failed_objects) > 0:
            print(f"Errors: {collection.batch.failed_objects}")

if __name__ == "__main__":
    try:
        setup_collection()
        process_minio_files()
    finally:
        client.close()