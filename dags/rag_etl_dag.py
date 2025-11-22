import requests
import io
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import weaviate
import weaviate.classes.config as wvc
from minio import Minio
from airflow import DAG
from airflow.operators.python import PythonOperator

# --- Configuration ---
# Service names inside Docker Network
MINIO_ENDPOINT = "minio:9000" 
WEAVIATE_ENDPOINT = "weaviate"
BUCKET_NAME = "airflow-rag-docs"
COLLECTION_NAME = "AirflowDocs"

# MinIO Credentials (ideally use Airflow Variables/Connections in prod)
MINIO_ACCESS_KEY = "minioadmin"
MINIO_SECRET_KEY = "minioadmin"

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

def get_minio_client():
    return Minio(
        MINIO_ENDPOINT,
        access_key=MINIO_ACCESS_KEY,
        secret_key=MINIO_SECRET_KEY,
        secure=False
    )

# --- Task 1: Scrape and Upload to MinIO ---
def scrape_to_minio(**kwargs):
    client = get_minio_client()
    
    # Ensure bucket exists
    if not client.bucket_exists(BUCKET_NAME):
        client.make_bucket(BUCKET_NAME)
        print(f"Created bucket: {BUCKET_NAME}")

    urls = [
        "https://airflow.apache.org/docs/apache-airflow/stable/core-concepts/dags.html",
        "https://airflow.apache.org/docs/apache-airflow/stable/core-concepts/operators.html"
    ]

    for i, url in enumerate(urls):
        try:
            print(f"Scraping: {url}")
            response = requests.get(url)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            content = soup.find('main') or soup.body
            text = content.get_text(separator='\n', strip=True)
            
            # Convert to bytes
            filename = f"doc_{i}.txt"
            data_bytes = text.encode('utf-8')
            data_stream = io.BytesIO(data_bytes)
            
            client.put_object(
                BUCKET_NAME,
                filename,
                data_stream,
                length=len(data_bytes),
                content_type="text/plain"
            )
            print(f"Uploaded {filename}")
            
        except Exception as e:
            print(f"Error on {url}: {e}")

# --- Task 2: Read from MinIO and Ingest to Weaviate ---
def ingest_from_minio(**kwargs):
    # Late imports to handle potential import errors gracefully during parse
    try:
        from langchain_text_splitters import RecursiveCharacterTextSplitter
    except ImportError:
        from langchain.text_splitter import RecursiveCharacterTextSplitter
    from sentence_transformers import SentenceTransformer

    minio_client = get_minio_client()
    
    # Connect to Weaviate
    print("Connecting to Weaviate...")
    weaviate_client = weaviate.connect_to_local(
        host=WEAVIATE_ENDPOINT,
        port=8080,
        grpc_port=50051
    )
    
    try:
        # Setup Collection
        if weaviate_client.collections.exists(COLLECTION_NAME):
            weaviate_client.collections.delete(COLLECTION_NAME)
        
        weaviate_client.collections.create(
            name=COLLECTION_NAME,
            vectorizer_config=wvc.Configure.Vectorizer.none(),
            properties=[
                wvc.Property(name="content", data_type=wvc.DataType.TEXT),
                wvc.Property(name="source", data_type=wvc.DataType.TEXT),
            ]
        )
        
        # Load Model (CPU)
        model = SentenceTransformer('all-MiniLM-L6-v2', device='cpu')
        splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        collection = weaviate_client.collections.get(COLLECTION_NAME)

        # List MinIO objects
        objects = minio_client.list_objects(BUCKET_NAME)
        
        for obj in objects:
            if not obj.object_name.endswith(".txt"):
                continue

            print(f"Downloading {obj.object_name}...")
            response = minio_client.get_object(BUCKET_NAME, obj.object_name)
            text = response.read().decode('utf-8')
            response.close()
            
            chunks = splitter.create_documents([text])
            
            with collection.batch.dynamic() as batch:
                for chunk in chunks:
                    vector = model.encode(chunk.page_content).tolist()
                    batch.add_object(
                        properties={
                            "content": chunk.page_content,
                            "source": f"minio://{BUCKET_NAME}/{obj.object_name}"
                        },
                        vector=vector
                    )
            print(f"Ingested {len(chunks)} chunks from {obj.object_name}")

    finally:
        weaviate_client.close()

# --- DAG ---
with DAG(
    'rag_minio_pipeline',
    default_args=default_args,
    schedule_interval='@daily',
    start_date=datetime(2024, 1, 1),
    catchup=False,
) as dag:

    t1 = PythonOperator(
        task_id='scrape_to_s3',
        python_callable=scrape_to_minio,
    )

    t2 = PythonOperator(
        task_id='s3_to_weaviate',
        python_callable=ingest_from_minio,
    )

    t1 >> t2