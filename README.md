# 🧠 Mini Enterprise AI Knowledge Assistant

[![CI/CD Pipeline](https://github.com/Pavan7856/AI-Knowledge-Assistant/actions/workflows/ci-cd.yml/badge.svg)](https://github.com/Pavan7856/AI-Knowledge-Assistant/actions/workflows/ci-cd.yml)
[![Python 3.11](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688.svg)](https://fastapi.tiangolo.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.32+-FF4B4B.svg)](https://streamlit.io/)
[![ChromaDB](https://img.shields.io/badge/ChromaDB-Vector_DB-7456C8.svg)](https://www.trychroma.com/)
[![Google Gemini](https://img.shields.io/badge/Google-Gemini_2.5_Flash-4285F4.svg)](https://aistudio.google.com/)
[![Docker](https://img.shields.io/badge/Docker-Containerized-2496ED.svg)](https://www.docker.com/)
[![Kubernetes](https://img.shields.io/badge/Kubernetes-Minikube-326CE5.svg)](https://kubernetes.io/)
[![Prometheus & Grafana](https://img.shields.io/badge/Monitoring-Prometheus_%26_Grafana-E6522C.svg)](https://grafana.com/)
[![Test Suite](https://img.shields.io/badge/Tests-34%20Passing-brightgreen.svg)](tests/)

An enterprise-grade, observable **Retrieval-Augmented Generation (RAG)** platform designed to ingest unstructured PDF documents, generate local dense vector embeddings, and answer complex user questions with verifiable page citations using **Google Gemini LLM**.

---

## 📑 Table of Contents
1. [System Architecture](#-system-architecture)
2. [Project Roadmap & Status](#-project-roadmap--status)
3. [Key Features](#-key-features)
4. [Project Directory Layout](#-project-directory-layout)
5. [Local Quickstart Guide](#-local-quickstart-guide)
6. [Docker & Containerized Deployment](#-docker--containerized-deployment)
7. [Kubernetes Orchestration (Minikube)](#-kubernetes-orchestration-minikube)
8. [Observability Stack (Prometheus, Grafana, Loki)](#-observability-stack)
9. [Automated CI/CD Pipeline](#-automated-cicd-pipeline)
10. [REST API Documentation](#-rest-api-documentation)
11. [Documentation & Interview Preparation](#-documentation--interview-preparation)

---

## 🏛️ System Architecture

```text
[ Web Browser ]
      │
      ▼
[ Streamlit UI (Port 8501) ]
      │
      ▼ (HTTP / REST)
[ FastAPI Backend (Port 8000) ]
   ├── PDF Text Extraction (PyMuPDF)
   ├── Recursive Text Chunker (700 chars / 150 overlap)
   ├── Local ONNX Embeddings (all-MiniLM-L6-v2, 384-dim)
   ├── Persistent Vector Database (ChromaDB)
   ├── Grounded Reasoning & Page Citations (Google Gemini 2.5 Flash)
   └── Metrics Instrumentation (Prometheus Client)
      │
      ├── Scrapes Metrics ──► [ Prometheus (Port 9090) ] ──► [ Grafana Dashboards (Port 3000) ]
      └── Ships Logs ───────► [ Grafana Alloy (Port 12345) ] ─► [ Loki (Port 3100) ]
```

> For deep architectural flowcharts and sequence diagrams, refer to [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).

---

## 📋 Project Roadmap & Status

- [x] **Phase 1: Environment & Basic Application** (FastAPI, Streamlit, PyMuPDF, Virtualenv)
- [x] **Phase 2: Complete RAG Pipeline** (LangChain Chunker, ChromaDB, Sentence Transformers, Gemini LLM)
- [x] **Phase 3: Docker Containerization** (Multi-container Dockerfiles, docker-compose, volume persistence)
- [x] **Phase 4: Kubernetes Deployment** (Deployments, Services, ConfigMaps, Secrets, PVCs, Minikube)
- [x] **Phase 5: Monitoring & Centralized Logging** (Prometheus, Grafana Dashboards, Loki, Grafana Alloy)
- [x] **Phase 6: CI/CD Automation** (GitHub Actions, Multi-stage cloud pipeline, automated testing)
- [x] **Phase 7: Final Assessment & Enterprise Deliverables** (Architecture specifications, presentation, interview guide)

---

## 🌟 Key Features

* **High-Accuracy RAG:** Local 384-dimensional dense vectors with cosine similarity retrieval.
* **Verifiable Auditability:** Every AI-synthesized answer directly cites the exact source file and page numbers.
* **Zero API Cost for Search:** Local ONNX embedding inference requires zero paid APIs or GPU hardware.
* **High Availability & Self-Healing:** Kubernetes deployments configure 2 replicas, liveness/readiness probes, and resource bounds.
* **Full Observability:** Prometheus scrapes real-time RPS, p95 latencies, and vector counts; Loki provides unified logging.
* **100% Automated Testing:** 34 comprehensive tests validating every component from unit logic to end-to-end user workflows.

---

## 📂 Project Directory Layout

```text
AI-Knowledge-Assistant/
├── backend/
│   ├── config.py              # Application settings & storage paths
│   ├── main.py                # FastAPI endpoints, middleware & Prometheus metrics
│   ├── pdf_processor.py       # PDF parsing & text extraction via PyMuPDF
│   ├── rag_pipeline.py        # LangChain chunking, ChromaDB & Gemini RAG logic
│   └── requirements.txt       # Backend microservice dependencies
├── frontend/
│   └── app.py                 # Streamlit UI with citations and Q&A interface
├── data/
│   └── uploads/               # Persistent PDF document storage
├── chroma_db/                 # Persistent Vector Database index
├── docs/
│   ├── ARCHITECTURE.md        # Technical architecture flowcharts & diagrams
│   ├── PRESENTATION.md        # Slide-by-slide presentation script
│   └── INTERVIEW_QA.md        # 14+ technical interview questions & detailed answers
├── k8s/
│   ├── backend-deployment.yaml# High-availability backend deployment (2 replicas)
│   ├── backend-service.yaml   # ClusterIP internal service
│   ├── frontend-deployment.yaml # High-availability Streamlit deployment
│   ├── frontend-service.yaml  # NodePort external service
│   ├── configmap.yaml         # Environment configurations
│   ├── secrets.yaml           # Secret management for Gemini API
│   ├── pvc.yaml               # PersistentVolumeClaims for storage
│   └── kustomization.yaml     # 1-click Kustomize deployment bundle
├── monitoring/
│   ├── prometheus/            # Prometheus scrape configuration
│   ├── loki/                  # Loki log storage configuration
│   ├── alloy/                 # Grafana Alloy log shipper pipeline
│   ├── grafana/               # Auto-provisioned datasources and custom dashboard JSON
│   └── docker-compose.monitoring.yml # Unified monitoring stack
├── tests/
│   ├── test_api.py            # FastAPI endpoints & PyMuPDF unit tests
│   ├── test_rag.py            # RAG chunking & vector retrieval tests
│   ├── test_docker_config.py  # Dockerfiles & compose syntax validation
│   ├── test_k8s_manifests.py  # Kubernetes manifests schema & probe tests
│   ├── test_monitoring.py     # Prometheus & Grafana dashboard tests
│   ├── test_github_actions.py # CI/CD workflow validation
│   └── test_ui_workflow.py    # Complete end-to-end user journey test
├── .github/workflows/
│   └── ci-cd.yml              # Multi-stage GitHub Actions CI/CD pipeline
├── Dockerfile.backend         # Production Dockerfile for FastAPI backend
├── Dockerfile.frontend        # Production Dockerfile for Streamlit frontend
├── docker-compose.yml         # Local application container orchestration
├── requirements.txt           # Consolidated project dependencies
└── README.md
```

---

## 🚀 Local Quickstart Guide

### 1. Setup Virtual Environment
```powershell
# Windows PowerShell
python -m venv .venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 2. Run Backend API
```powershell
# Terminal 1
.\.venv\Scripts\uvicorn.exe backend.main:app --reload --port 8000
```
* **Swagger API Documentation:** [http://localhost:8000/docs](http://localhost:8000/docs)
* **Prometheus Metrics:** [http://localhost:8000/metrics](http://localhost:8000/metrics)

### 3. Run Frontend UI
```powershell
# Terminal 2
.\.venv\Scripts\streamlit.exe run frontend/app.py
```
* **Web UI:** [http://localhost:8501](http://localhost:8501)

---

## 🐳 Docker & Containerized Deployment

Run the complete multi-container application with healthchecks and persistent storage:

```bash
# Build and start all containers in background
docker-compose up -d --build

# View container status
docker-compose ps

# Stream logs
docker-compose logs -f
```

---

## ☸️ Kubernetes Orchestration (Minikube)

Deploy high-availability Pods (2 replicas each) with Persistent Volume Claims to local Minikube:

```powershell
# 1. Start Minikube cluster
minikube start --cpus=4 --memory=6144

# 2. Deploy all resources via Kustomize
kubectl apply -k k8s/

# 3. Verify running Pods and Services
kubectl get pods
kubectl get services
kubectl get pvc

# 4. Open frontend in browser
minikube service frontend-service
```

---

## 📊 Observability Stack

Launch Prometheus, Grafana, Loki, and Grafana Alloy in one command:

```powershell
docker-compose -f monitoring/docker-compose.monitoring.yml up -d
```
* **Grafana Dashboards:** [http://localhost:3000](http://localhost:3000) *(Credentials: `admin` / `admin`)*
* **Prometheus Target Metrics:** [http://localhost:9090](http://localhost:9090)
* **Loki Log Ingestion:** [http://localhost:3100](http://localhost:3100)

---

## 🔄 Automated CI/CD Pipeline

The GitHub Actions workflow ([.github/workflows/ci-cd.yml](.github/workflows/ci-cd.yml)) runs automatically on every commit:
1. **Testing:** Executes the full 34-test suite using Python 3.11 with pip caching.
2. **Container Build:** Compiles and validates `Dockerfile.backend` and `Dockerfile.frontend`.
3. **K8s Dry-Run:** Runs `kubectl apply --dry-run=client -k k8s/` to verify zero Kubernetes manifest schema violations.

---

## 📡 REST API Documentation

| Method | Endpoint | Description | Payload / Query |
| :--- | :--- | :--- | :--- |
| `GET` | `/health` | Live service health & vector count | None |
| `GET` | `/metrics` | Prometheus metrics for scraping | None |
| `POST` | `/api/upload-pdf` | Ingests, parses, chunks & indexes PDF | `multipart/form-data` with `file` |
| `POST` | `/api/query` | RAG semantic search & LLM generation | `{"question": "string", "top_k": 3}` |
| `GET` | `/api/documents` | Lists indexed documents | None |
| `POST` | `/api/set-gemini-key` | Sets or updates Gemini API key | `{"api_key": "string"}` |
| `POST` | `/api/reset-database` | Clears all vector embeddings | None |

---

## 📚 Documentation & Interview Preparation

* 🏛️ **[Technical Architecture Specifications](docs/ARCHITECTURE.md):** In-depth sequence flows, security considerations, and component diagrams.
* 📽️ **[Slide-by-Slide Presentation Guide](docs/PRESENTATION.md):** Complete presentation script for technical evaluations and client demonstrations.
* 🎯 **[Enterprise Technical Interview Q&A](docs/INTERVIEW_QA.md):** 14+ in-depth technical questions and answers covering RAG, embeddings, Docker, Kubernetes, and Observability.

---

## 👤 Author & Maintainer
* **Author:** Pavan Rathod
* **Email:** pavanrathod7856@gmail.com
* **GitHub Repository:** [https://github.com/Pavan7856/AI-Knowledge-Assistant](https://github.com/Pavan7856/AI-Knowledge-Assistant)
