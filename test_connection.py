import weaviate
from minio import Minio
import os

print("--- Testing Weaviate Connection ---")
try:

    client = weaviate.connect_to_custom( 
        http_host="localhost",
        http_port=8090,  # The HTTP port from docker-compose
        http_secure=False,
        grpc_host="localhost",
        grpc_port=50051,  # The gRPC port from docker-compose
        grpc_secure=False,
    )
    
    if client.is_live():
        print("✅ Weaviate v4 client is READY!")
    else:
        print("❌ Weaviate v4 client is NOT ready.")
    
    client.close()

except Exception as e:
    print(f"❌ FAILED to connect to Weaviate: {e}")

print("\n--- Testing MinIO Connection ---")
try:
    minio_client = Minio(
        "localhost:9000",
        access_key="minioadmin",
        secret_key="minioadmin",
        secure=False
    )
    if not minio_client.bucket_exists("test-bucket"):
        print("✅ MinIO: Connection OK. (Note: 'test-bucket' doesn't exist yet, which is normal).")
except Exception as e:
    print(f"❌ FAILED to connect to MinIO: {e}")