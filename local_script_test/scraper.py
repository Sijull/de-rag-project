import requests
from bs4 import BeautifulSoup
import io
from minio import Minio

# --- Configuration ---
# Connect to localhost because this script runs on your laptop
MINIO_CLIENT = Minio(
    "localhost:9000",
    access_key="minioadmin",  # Default, change if you set specific env vars
    secret_key="minioadmin",  
    secure=False
)
BUCKET_NAME = "rag-raw-data"

URLS = [
    "https://airflow.apache.org/docs/apache-airflow/stable/core-concepts/dags.html",
    "https://airflow.apache.org/docs/apache-airflow/stable/core-concepts/operators.html",
    "https://airflow.apache.org/docs/apache-airflow/stable/core-concepts/tasks.html"
]

def setup_bucket():
    if not MINIO_CLIENT.bucket_exists(BUCKET_NAME):
        MINIO_CLIENT.make_bucket(BUCKET_NAME)
        print(f"Bucket '{BUCKET_NAME}' created.")
    else:
        print(f"Bucket '{BUCKET_NAME}' already exists.")

def scrape_and_upload(urls):
    setup_bucket()
    
    for i, url in enumerate(urls):
        try:
            print(f"Scraping: {url}")
            response = requests.get(url)
            soup = BeautifulSoup(response.content, 'html.parser')

            content = soup.find('main') or soup.body
            text = content.get_text(separator='\n', strip=True)
            
            # Prepare filename and data
            filename = f"doc_{i}.txt"
            # Convert string to bytes for MinIO
            data_bytes = text.encode('utf-8')
            data_stream = io.BytesIO(data_bytes)
            
            # Upload to MinIO
            MINIO_CLIENT.put_object(
                BUCKET_NAME,
                filename,
                data_stream,
                length=len(data_bytes),
                content_type="text/plain"
            )
            print(f"Uploaded {filename} to MinIO")
            
        except Exception as e:
            print(f"Failed to process {url}: {e}")

if __name__ == "__main__":
    scrape_and_upload(URLS)