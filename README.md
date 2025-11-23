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

*(This section is a placeholder for your future self. You'll fill this in after Weekend 1-2)*

This project is 100% reproducible using Docker.
