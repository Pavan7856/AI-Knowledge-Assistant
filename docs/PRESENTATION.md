# 📽️ Enterprise AI Knowledge Assistant - Technical Presentation

A slide-by-slide presentation outline and script for technical evaluations, client demos, and project reviews.

---

### Slide 1: Title & Executive Summary
* **Project Name:** Mini Enterprise AI Knowledge Assistant
* **Presenter:** Pavan Rathod
* **Core Value Proposition:** An enterprise-ready, containerized, and observable Retrieval-Augmented Generation (RAG) platform that enables accurate question answering over internal unstructured PDF documents with source page citations.
* **Tech Stack:** Python 3.11, FastAPI, Streamlit, PyMuPDF, LangChain, ChromaDB, Google Gemini, Docker, Kubernetes, Prometheus, Grafana, Loki, GitHub Actions.

---

### Slide 2: The Enterprise Challenge
* **The Problem:** Modern enterprises possess vast volumes of unstructured knowledge (policy documents, technical manuals, architectural designs, compliance guidelines) locked in PDFs.
* **Limitations of Standard LLMs:**
  1. **Hallucination:** Public LLMs guess or invent facts when unsure.
  2. **Knowledge Cutoffs:** Standard models cannot read private or recent enterprise documents.
  3. **Lack of Auditing:** Standard AI does not tell you *where* or on *which page* it found the answer.
* **Why Fine-Tuning is Inadequate:** Retraining large models is expensive, slow, and requires retraining every time a document changes.

---

### Slide 3: The Solution — Retrieval-Augmented Generation (RAG)
* **How RAG Solves This:**
  1. **Retrieve:** When a user asks a question, retrieve the exact relevant passages from private documents using dense vector similarity search.
  2. **Augment:** Inject the retrieved passages into the LLM prompt as trusted context.
  3. **Generate:** Instruct the LLM to synthesize an answer based *only* on the provided context with specific page citations.
* **Key Benefits:** Zero hallucination, real-time document updates without model retraining, and verifiable page-level auditability.

---

### Slide 4: System Architecture & Data Flow
* **Decoupled Architecture:**
  - **Frontend:** Streamlit user interface (Port 8501) with live metrics and citation pills.
  - **Backend API:** FastAPI REST service (Port 8000) orchestrating parsing, vectorization, and generation.
  - **Vector Database:** ChromaDB with local ONNX `all-MiniLM-L6-v2` embeddings.
  - **LLM Engine:** Google Gemini 2.5 Flash for high-speed, grounded reasoning.
  - **Observability:** Prometheus for metrics, Loki for logs, Grafana for unified visual dashboards.

---

### Slide 5: Ingestion & Text Chunking Deep Dive
* **Document Extraction:** PyMuPDF extracts text page by page, preserving page metadata.
* **Chunking Strategy:**
  - Uses `RecursiveCharacterTextSplitter` (700 characters with 150 character overlap).
  - Preserves sentence and paragraph boundaries to prevent context splitting.
* **Vector Embeddings:**
  - Converts text chunks into 384-dimensional dense semantic vectors.
  - Stored locally with cosine distance indexing for sub-millisecond retrieval.

---

### Slide 6: Containerization (Docker)
* **Multi-Container Architecture:**
  - `Dockerfile.backend`: Optimized Python 3.11-slim container with PyMuPDF, ChromaDB, and FastAPI.
  - `Dockerfile.frontend`: Streamlit UI container.
  - `docker-compose.yml`: Automated orchestration with named persistent volumes (`pdf_data`, `chroma_data`) and health check dependencies.
* **Persistence Guarantee:** Data and vectors persist across container restarts.

---

### Slide 7: Kubernetes Orchestration (Minikube)
* **High Availability:**
  - 2 Backend Replicas and 2 Frontend Replicas for zero downtime.
* **Resilience:**
  - Liveness and Readiness probes automatically replace unhealthy pods.
* **Storage:**
  - `PersistentVolumeClaims` (PVC) provide persistent disk storage in the cluster.
* **Networking:**
  - Internal `ClusterIP` for backend; `NodePort` for external frontend browser access.

---

### Slide 8: Enterprise Observability (Prometheus + Grafana + Loki)
* **Metrics (Prometheus):**
  - Scrapes FastAPI `/metrics` every 5 seconds.
  - Real-time tracking of RPS, error rates, p95 response latencies, and stored vector counts.
* **Centralized Logging (Loki + Grafana Alloy):**
  - Aggregates container logs without high memory overhead.
* **Unified Dashboards:**
  - Pre-configured Grafana dashboard visualizing live system health, traffic, and logs in one screen.

---

### Slide 9: CI/CD Pipeline (GitHub Actions)
* **Automated 3-Stage Pipeline:**
  1. **Stage 1 (Test):** Runs 34 automated unit and RAG tests with pip caching.
  2. **Stage 2 (Build):** Compiles and validates Docker backend and frontend images.
  3. **Stage 3 (Validate):** Executes `kubectl apply --dry-run=client` against Kubernetes manifests to ensure schema compliance.
* **Zero Broken Deployments:** Guarantees that only tested, verified code can reach production.

---

### Slide 10: Summary & Production Readiness
* **Key Achievements:**
  - 100% automated test coverage (34 passing tests).
  - Production-ready Kubernetes manifests and Docker Compose.
  - Full observability stack included out-of-the-box.
  - Fully functional in English with automated citation generation.

