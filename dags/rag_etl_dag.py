import os
import requests
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import weaviate
import weaviate.classes.config as wvc
from airflow import DAG
from airflow.operators.python import PythonOperator

# --- Configuration ---
# We save data to 'dags/data' so it is visible on your host machine too
DATA_PATH = "/opt/airflow/dags/data/rag_docs"
WEAVIATE_URL = "weaviate"  # Service name in docker-compose (NOT localhost)
WEAVIATE_PORT = 8090
COLLECTION_NAME = "AirflowDocs"

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# --- Task 1: Scrape Data ---
def scrape_data(**kwargs):
    urls = [
        "https://airflow.apache.org/docs/apache-airflow/stable/core-concepts/dags.html",
        "https://airflow.apache.org/docs/apache-airflow/stable/core-concepts/operators.html",
        "https://airflow.apache.org/docs/apache-airflow/stable/core-concepts/tasks.html"
    ]
    
    # Create directory if it doesn't exist
    if not os.path.exists(DATA_PATH):
        os.makedirs(DATA_PATH)

    for i, url in enumerate(urls):
        try:
            print(f"Scraping: {url}")
            response = requests.get(url)
            soup = BeautifulSoup(response.content, 'html.parser')

            # Basic content extraction
            content = soup.find('main') or soup.body
            text = content.get_text(separator='\n', strip=True)
            
            filename = f"{DATA_PATH}/doc_{i}.txt"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(f"Source: {url}\n\n")
                f.write(text)
            print(f"Saved {filename}")
            
        except Exception as e:
            print(f"Failed to scrape {url}: {e}")

# --- Task 2: Embed & Ingest ---
def embed_and_ingest(**kwargs):
    # Import here to avoid top-level errors if libs are missing during initial parse
    # Try the new import, fallback to old if necessary
    try:
        from langchain_text_splitters import RecursiveCharacterTextSplitter
    except ImportError:
        from langchain.text_splitter import RecursiveCharacterTextSplitter
        
    from sentence_transformers import SentenceTransformer
    
    print(f"Connecting to Weaviate at {WEAVIATE_URL}...")
    client = weaviate.connect_to_local(
        host=WEAVIATE_URL,
        port=WEAVIATE_PORT,
        grpc_port=50051
    )
    
    try:
        # 1. Setup Collection
        if client.collections.exists(COLLECTION_NAME):
            client.collections.delete(COLLECTION_NAME)
            print(f"Deleted existing collection: {COLLECTION_NAME}")
            
        client.collections.create(
            name=COLLECTION_NAME,
            vectorizer_config=wvc.Configure.Vectorizer.none(),
            properties=[
                wvc.Property(name="content", data_type=wvc.DataType.TEXT),
                wvc.Property(name="source", data_type=wvc.DataType.TEXT),
            ]
        )
        print("Created new collection.")

        # 2. Load Model (Force CPU)
        # Since we installed cpu-only torch, this will run efficiently
        print("Loading embedding model on CPU...")
        model = SentenceTransformer('all-MiniLM-L6-v2', device='cpu')
        splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        
        collection = client.collections.get(COLLECTION_NAME)

        # 3. Process Files
        if not os.path.exists(DATA_PATH):
            print(f"No data found at {DATA_PATH}")
            return

        files = [f for f in os.listdir(DATA_PATH) if f.endswith('.txt')]
        print(f"Found {len(files)} files to process.")

        for filename in files:
            file_path = os.path.join(DATA_PATH, filename)
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
            
            chunks = splitter.create_documents([text])
            print(f"Processing {filename}: {len(chunks)} chunks")

            with collection.batch.dynamic() as batch:
                for chunk in chunks:
                    vector = model.encode(chunk.page_content).tolist()
                    batch.add_object(
                        properties={
                            "content": chunk.page_content,
                            "source": filename
                        },
                        vector=vector
                    )
            
            if len(collection.batch.failed_objects) > 0:
                print(f"Errors in {filename}: {collection.batch.failed_objects}")
            else:
                print(f"Successfully ingested {filename}")

    finally:
        client.close()

# --- DAG Definition ---
with DAG(
    'rag_ingestion_pipeline',
    default_args=default_args,
    description='Scrapes docs and ingests into Weaviate',
    schedule_interval='@daily', # Run once a day
    start_date=datetime(2024, 1, 1),
    catchup=False,
) as dag:

    t1 = PythonOperator(
        task_id='scrape_docs',
        python_callable=scrape_data,
    )

    t2 = PythonOperator(
        task_id='embed_and_ingest',
        python_callable=embed_and_ingest,
    )

    t1 >> t2