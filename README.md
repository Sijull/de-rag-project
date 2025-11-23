# de-rag-project
This is my first project exploring RAG in a POV of Data Engineer

# Private-RAG: An End-to-End GenAI Data Pipeline

[![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python&logoColor=white)](https://www.python.org/)
[![Airflow](https://img.shields.io/badge/Airflow-2.8.0-blue?logo=apacheairflow&logoColor=white)](https://airflow.apache.org/)
[![Docker](https://img.shields.io/badge/Docker-blue?logo=docker&logoColor=white)](https://www.docker.com/)
[![Ollama](https://img.shields.io/badge/Ollama-black?logo=ollama&logoColor=white)](https://ollama.com/)
[![Weaviate](https://img.shields.io/badge/Weaviate-green?logo=weaviate&logoColor=white)](https://weaviate.io/)

This project is an end-to-end, production-grade RAG (Retrieval-Augmented Generation) pipeline built from scratch using 100% open-source tools. It is designed to be fully private, highly customizable, and architected for a real-world, cost-effective cloud deployment.

---

## 🚀 Live Demo

![1122 (1)](https://github.com/user-attachments/assets/d70bcf93-22dd-4b8b-8f96-44fc4230b468)


---

## 🎯 The Core Problem & Project Goal

Public APIs like OpenAI are powerful but present three fundamental business risks: **data privacy**, **cost control**, and **model lock-in**.

This project solves those problems by architecting a system where:

1. **Data is 100% Private:** No proprietary data ever leaves the local network or private cloud (VPC).

2. **Costs are Fixed & Predictable:** It uses a self-hosted model, avoiding the massive, unpredictable "per-token" costs of an API at scale.

3. **The System is 100% Controllable:** Every component is open-source, avoiding vendor lock-in. This allows for deep customization, such as fine-tuning a specialized model to outperform a generic one.

## 🛠️ Tech Stack

| Category | Tool | Purpose | 
 | ----- | ----- | ----- | 
| **Orchestration** | **Apache Airflow** | Manages and schedules the entire data ingestion pipeline (scrape, chunk, embed, load). | 
| **Containerization** | **Docker Compose** | Defines and runs the entire multi-service application (DBs, apps, services). | 
| **Data Lake** | **MinIO** | S3-compatible object storage for raw ingested articles. | 
| **Vector Database** | **Weaviate** | Stores vector embeddings and their corresponding text chunks for similarity search. | 
| **LLM Hosting** | **Ollama (`phi3:mini`)** | Serves the open-source LLM, using the host's GPU for accelerated inference. | 
| **Processing** | **LangChain** | Used for document loading and text chunking. | 
| **Embedding Model** | **Sentence-Transformers** | A local model that creates vector embeddings from text chunks. | 
| **Backend API** | **FastAPI** | Serves a single `/chat` endpoint to perform the RAG query. | 
| **Frontend UI** | **Streamlit** | Provides a simple, clean web interface for chatting with the data. | 

## 🏗️ Architecture

This project was built locally with a 1-to-1 migration path to a cost-effective, hybrid cloud model.

### 1. System Architecture

This is the system running on the local machine. It uses Docker's `host.docker.internal` to allow the containers to access the GPU-accelerated Ollama server running on the host.
<img width="1959" height="1196" alt="Diagram Tanpa Judul drawio (3)" src="https://github.com/user-attachments/assets/0bf36bf6-e457-4060-a24b-020f86fa4a03" />


## 📈 Project Status & Log

This project is being built using a weekend-based phased plan.

* **\[✅\] Weekend 1: Service Plumbing**

  * **Goal:** Get all 6 services (Airflow, Postgres, MinIO, Weaviate, FastAPI, Streamlit) running and communicating in `docker-compose`.

  * **Result:** Success. All containers are green. The Airflow UI, MinIO UI, and Streamlit UI are accessible. The API-to-Ollama connection is confirmed using `host.docker.internal` and the `/test-ollama` endpoint.

* **\[✅\] Weekend 2: The RAG "Brain"**

  * **Goal:** Build the core RAG logic as standalone Python scripts (`process.py`, `query.py`).

  * **Result:** Success. All scripts working properly. The `scraper.py` scrape the data from the URL and store it into MinIO bucket, the `process.py` successfully create embedding model from data chunks, the `query.py` is running the LLM models can read the context from weaviate.

* **\[✅\] Weekend 3: Airflow Orchestration**

  * **Goal:** Move the RAG logic into a formal Airflow DAG.

  * **Result:** The raw ingestion and vectorizing the data succesfully move into DAG and now its scheduled

* **\[✅\] Weekend 4: The "Showcase"**

  * **Goal:** Finalize the FastAPI & Streamlit apps for a clean user experience.

  * **Result:** The API and Chat UI page works perfectly and ready to use.

## ⚙️ How to Run This Project

This project is 100% reproducible using Docker. Here is the step by step to start this system.

1. first you can copy or fork this repository. i recommend to install python virtual environtment while working or starting this project.
  Please spare at least 30GB storage space for the docker containers. Install all requirements like Ollama and Docker on you computer.

2. Prepare the .env variables you can use the template in the example. generate fernet key for AIRLFLOW__CORE__FERNET_KEY by running this in terminal:
  ```
  python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
  ```

3. Before you run the docker compose you must setup the ollama you can install ollama on your local machine.
   After installation success open your termimal and run this to verify you ollama installaion
   ```
   ollama --version
   ```
   you can see you ollama version if your installation is success then we get our model the phi3:mini by running this command
   ```
   ollama pull phi3:mini
   ```
   after the download success you can run this commnand so that our docker service can use the model from our local machine
   ```
   ollama serve
   ```
   
5. If all the env var is set and you local model is set you can run docker build command. this can take time up to 30-45 minutes you can make a coffee while waiting this to finish. open terminal in project folder.
   ```
   docker compose up --build
   ```
   
6. After docker compose is up you can check all the service by open it on the broser with `localhost:[the service ports]` you can check all the ports on docker-compose.yml file
   
7. If all the components run you can test it by running all scrips int he local_script_test folder. run all this command
   ```
   pip install -r requirements.txt
   python run scraper.py
   python run process.py
   python run query.py
   ```
   You can verify all the service running after running all of this script make sure you run this command on local_script_test folder.
   
8. After you test it on a local you can access the UI streamlit and began chatting with the LLM model.

## 🌐 Accessing Services
Once all containers are running, you can access the different UIs in your browser:

- RAG App (Streamlit): `http://localhost:8501`

- Apache Airflow UI: `http://localhost:8080`

- User: airflow

- Pass: airflow

- MinIO UI: `http://localhost:9001`

- User/Pass: (As defined in your .env file)

## 🔮 Future Ideas (The "Icebox") and Room for Improvment
This is a list of features intentionally not built to manage scope, but which could be added later:

- Support for PDF and .docx file uploads.

- A "Fine-Tuning" DAG for the phi3:mini model.

- User authentication for the Streamlit app.

- Migrating from Weaviate to pgvector for an all-Postgres solution.

- Use cloud service like S3 to replace minio or SageMaker for cloud solution of LLM model management

- Use kubernetes to manage our docker container
