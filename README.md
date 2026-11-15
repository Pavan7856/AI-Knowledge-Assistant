# 📚 Mini Enterprise AI Knowledge Assistant

An Enterprise-grade PDF Knowledge Assistant leveraging **Retrieval-Augmented Generation (RAG)**, **FastAPI**, **Streamlit**, **ChromaDB**, and **Google Gemini LLM**, fully containerized and orchestrated with **Docker** and **Kubernetes**, monitored via **Prometheus & Grafana**.

---

## 🏗️ Project Architecture Overview

```text
[ User / Browser ]
        │
        ▼
[ Streamlit UI (Port 8501) ]
        │
        ▼ (HTTP / REST)
[ FastAPI Backend (Port 8000) ]
   ├── PDF Text Extraction (PyMuPDF)
   ├── Chunking & Embeddings (Sentence Transformers)
   ├── Vector Storage & Similarity Search (ChromaDB)
   └── Contextual Q&A (Google Gemini API)
```

---

## 📂 Project Structure

```text
AI-Knowledge-Assistant/
├── backend/
│   ├── config.py              # Application settings & storage paths
│   ├── pdf_processor.py       # PDF parsing & text extraction via PyMuPDF
│   ├── main.py                # FastAPI endpoints (upload, parse, health)
│   ├── rag_pipeline.py        # RAG pipeline implementation (Phase 2)
│   └── requirements.txt       # Backend dependencies
├── frontend/
│   └── app.py                 # Streamlit User Interface
├── data/
│   └── uploads/               # Persistent PDF document storage
├── chroma_db/                 # Persistent Vector Database store (Phase 2)
├── tests/
│   ├── test_api.py            # Automated API and ingestion unit tests
│   └── test_rag.py            # RAG accuracy and retrieval tests (Phase 2)
├── monitoring/                # Observability configuration (Phase 5)
├── k8s/                       # Kubernetes deployment manifests (Phase 4)
├── .github/workflows/         # CI/CD GitHub Actions pipelines (Phase 6)
├── requirements.txt           # Full project dependencies
└── README.md
```

---

## 🚀 Phase 1: Quickstart Guide (Local Setup)

### 1. Activate Virtual Environment
```powershell
# Windows PowerShell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

### 2. Run the FastAPI Backend Server
Open **Terminal 1**:
```powershell
.\.venv\Scripts\uvicorn.exe backend.main:app --reload --port 8000
```
- Swagger API Docs: [http://localhost:8000/docs](http://localhost:8000/docs)
- Health Check: [http://localhost:8000/health](http://localhost:8000/health)

### 3. Run the Streamlit Frontend Interface
Open **Terminal 2**:
```powershell
.\.venv\Scripts\streamlit.exe run frontend/app.py
```
- Frontend Web UI: [http://localhost:8501](http://localhost:8501)

---

## 🐳 Phase 3: Docker & Docker Compose Setup

Run both services with persistent storage and healthchecks using Docker Compose:

```bash
# Build and start all containers in the background
docker-compose up -d --build

# Inspect running containers
docker-compose ps

# View real-time container logs
docker-compose logs -f

# Stop all containers
docker-compose down
```

---

## ☸️ Phase 4: Kubernetes Deployment (Minikube)

Deploy the entire enterprise system to local Kubernetes using Minikube:

### 1. Start Local Cluster
```powershell
minikube start --cpus=4 --memory=6144
```

### 2. Deploy All Resources (1-Click Kustomize)
```powershell
kubectl apply -k k8s/
```

### 3. Verify Pods and Services
```powershell
# View running pods (2 backend replicas, 2 frontend replicas)
kubectl get pods

# View cluster services and NodePorts
kubectl get services

# View persistent storage volumes
kubectl get pvc
```

### 4. Access the Streamlit Frontend via Minikube
```powershell
minikube service frontend-service
```

---

## 📊 Phase 5: Monitoring & Centralized Observability

Launch the enterprise observability stack (Prometheus, Grafana, Loki, Grafana Alloy):

```powershell
# Start all monitoring services
docker-compose -f monitoring/docker-compose.monitoring.yml up -d

# Service Endpoints:
# - Prometheus Metrics: http://localhost:9090
# - Grafana Dashboards: http://localhost:3000 (User: admin, Pass: admin)
# - Loki Log Ingestion: http://localhost:3100
# - Grafana Alloy UI:   http://localhost:12345
```

---

## 🔄 Phase 6: Automated CI/CD Pipeline (GitHub Actions)

The pipeline ([.github/workflows/ci-cd.yml](.github/workflows/ci-cd.yml)) automatically triggers on every `push` or `pull_request` to `main`:

```text
[ Git Push / PR ]
       │
       ▼
┌──────────────────────────────────────────────┐
│ Stage 1: Automated Testing                   │
│ - Sets up Python 3.11 with pip caching       │
│ - Executes 34 automated unit & RAG tests     │
└──────────────────────┬───────────────────────┘
                       │ (On Success)
                       ▼
┌──────────────────────────────────────────────┐
│ Stage 2: Container Verification              │
│ - Builds Dockerfile.backend image            │
│ - Builds Dockerfile.frontend image           │
└──────────────────────┬───────────────────────┘
                       │ (On Success)
                       ▼
┌──────────────────────────────────────────────┐
│ Stage 3: Kubernetes Validation               │
│ - Dry-run validation of all 7 K8s manifests  │
│ - Confirms zero schema violations            │
└──────────────────────────────────────────────┘
```

---

## 📋 Implementation Roadmap

- [x] **Phase 1: Environment & Basic Application** (FastAPI, Streamlit, PyMuPDF, Folder Setup)
- [x] **Phase 2: RAG Pipeline Implementation** (Text Chunking, Sentence Transformers, ChromaDB, Gemini LLM)
- [x] **Phase 3: Docker Containerization** (Dockerfile, docker-compose)
- [x] **Phase 4: Kubernetes Deployment** (Minikube, Deployments, Services, PVC)
- [x] **Phase 5: Monitoring & Centralized Logging** (Prometheus, Grafana, Loki, Grafana Alloy)
- [x] **Phase 6: CI/CD Automation** (GitHub Actions)
- [ ] **Phase 7: Final Assessment & Enterprise Deliverables**

