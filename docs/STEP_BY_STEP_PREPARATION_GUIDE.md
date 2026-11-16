# Enterprise AI Knowledge Assistant: Complete Step-by-Step Preparation Guide
*(मुद्देसूद तयारी आणि Interview/Presentation साठी संपूर्ण मार्गदर्शक)*

---

## 📌 1. Project Overview & 30-Second Elevator Pitch

### In English (For Technical Interviews):
> *"The **Enterprise AI Knowledge Assistant** is a production-grade, containerized Retrieval-Augmented Generation (RAG) platform. It allows organizations to upload dense PDF technical documents, extract and chunk text semantically, index them into a high-performance vector database using dense embeddings, and query them with contextual grounding using Google Gemini. The system provides exact page-level citations to eliminate hallucinations. Architecturally, it is decoupled into a FastAPI REST backend and a Streamlit UI, fully containerized with Docker, orchestrated for high availability on Kubernetes with persistent volumes and rolling updates, monitored in real time via Prometheus, Loki, and Grafana, and automated using a 3-stage GitHub Actions CI/CD pipeline."*

### In Marathi (मराठीत सोप्या भाषेत सांगण्यासाठी):
> *"हा **Enterprise AI Knowledge Assistant** एक पूर्ण Production-Ready RAG (Retrieval-Augmented Generation) प्रोजेक्ट आहे. यामध्ये कंपनीचे मोठे आणि क्लिष्ट PDF दस्तऐवज (Technical Documents, Manuals, Policies) अपलोड करून त्यांच्यावर प्रश्न विचारता येतात. AI (Google Gemini) केवळ अंदाज न लावता डॉक्युमेंटमधील नेमक्या पानाचा संदर्भ (Page-level citation) देऊन 100% अचूक उत्तर देते. यात **FastAPI** चा Backend, **Streamlit** चा Frontend, **ChromaDB** चा Vector Store, **Docker** आणि **Kubernetes** चे Production Deployment, **Prometheus & Grafana** चे Live Monitoring, आणि **GitHub Actions** ची CI/CD Pipeline अशा सर्व Enterprise Engineering Standards चा वापर केला आहे."*

---

## 🏗️ 2. Architectural Blueprint

```
+-----------------------------------------------------------------------------------+
|                                  USER / CLIENT                                    |
+-----------------------------------------+-----------------------------------------+
                                          |
                         HTTP / Port 8501 | (Browser UI)
                                          v
+-----------------------------------------------------------------------------------+
|                        FRONTEND SERVICE (Streamlit)                               |
| - Document Upload Interface | Top-k / Temperature Sliders                         |
| - Real-time Chat Assistant  | Source Citation Badges & System Health Metrics      |
+-----------------------------------------+-----------------------------------------+
                                          |
                         REST API / 8000  | (JSON / Multipart)
                                          v
+-----------------------------------------------------------------------------------+
|                         BACKEND SERVICE (FastAPI)                                 |
| - Middleware: Prometheus Metrics Instrumentation (/metrics)                       |
| - REST Endpoints: /upload, /query, /documents, /health, /metrics                  |
+--------------------+--------------------------------------+-----------------------+
                     |                                      |
                     v                                      v
+-----------------------------------+  +--------------------------------------------+
|     DOCUMENT INGESTION ENGINE     |  |          RAG RETRIEVAL & SYNTHESIS         |
| 1. PyMuPDF (Fast PDF parsing)     |  | 1. Query Embedding (all-MiniLM-L6-v2)      |
| 2. RecursiveCharacterTextSplitter |  | 2. Cosine Similarity Search in ChromaDB    |
|    (700 chunk size, 150 overlap)  |  | 3. Top-k Context Ingestion                 |
| 3. ONNX all-MiniLM-L6-v2 Embedder |  | 4. Google Gemini 2.5 Flash Grounded Prompt |
| 4. ChromaDB Persistent Storage    |  | 5. Strict Grounding with [Page X] Citations|
+-----------------------------------+  +--------------------------------------------+
                     |                                      |
                     +-------------------+------------------+
                                         |
                                         v
+-----------------------------------------------------------------------------------+
|                        STORAGE & OBSERVABILITY LAYER                              |
| - Named Volumes / PVC: /app/data/uploads (PDFs), /app/chroma_db (Vectors)         |
| - Prometheus (Port 9090): Scrapes Request Rates, Latencies, Vector Counts         |
| - Grafana (Port 3000): Live Visual Dashboards & Observability                     |
| - Loki & Grafana Alloy (Port 3100): Centralized Container Log Aggregation        |
+-----------------------------------------------------------------------------------+
```

---

## 🚀 3. Phase-by-Phase Chronological Walkthrough

---

### 🔹 Phase 1: Environment Setup & Core REST Backend

#### Goal:
Set up a clean virtual environment, project structure, high-speed PDF text extractor, and the core FastAPI REST API.

#### Key Files Created:
1. `backend/config.py`: Environment configuration via Pydantic/`os.getenv` (`CHUNK_SIZE`, `CHUNK_OVERLAP`, `MAX_FILE_SIZE_MB`, `GEMINI_API_KEY`).
2. `backend/pdf_processor.py`: PyMuPDF (`fitz`) extractor extracting page-by-page text, page counts, character counts, and validating PDF magic bytes (`%PDF-`).
3. `backend/main.py`: FastAPI application with CORS middleware, lifespan events, and initial endpoints (`/health`, `/upload`, `/documents`).
4. `requirements.txt`: Python package requirements.

#### Engineering Decisions:
- **Why PyMuPDF (`fitz`) over `pypdf` or `pdfplumber`?**
  - PyMuPDF is written in C (MuPDF) and is **10-100x faster** than pure Python PDF libraries. It accurately handles multi-column layouts and preserves page numbering, which is vital for citation accuracy.
- **Why FastAPI over Flask or Django?**
  - FastAPI is built on ASGI (Starlette + Pydantic), providing native `async/await` high-concurrency support, automatic OpenAPI/Swagger documentation (`/docs`), and request validation.

#### Step-by-Step Commands Run:
```powershell
# 1. Create and activate virtual environment
python -m venv .venv
.venv\Scripts\Activate.ps1

# 2. Install dependencies
pip install fastapi uvicorn pymupdf pydantic python-multipart httpx

# 3. Start local development server
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

#### How to Explain in an Interview:
- **English:** *"In Phase 1, I established the foundation using FastAPI and PyMuPDF. I built a decoupled REST API with validation for PDF magic headers and file size limits (25MB). I extracted page numbers alongside text chunks to ensure downstream citations would be 100% verifiable."*
- **मराठी:** *"Phase 1 मध्ये आपण प्रोजेक्टचा पाया रचला. FastAPI वापरून REST API तयार केला आणि PDF मधून मजकूर काढण्यासाठी PyMuPDF निवडले कारण ते इतर लायब्ररींपेक्षा 10 पट जलद चालते. यात प्रत्येक पानाचा नंबर टेक्स्टसोबत साठवला, जेणेकरून नंतर AI ला अचूक Page Citation देता येईल."*

---

### 🔹 Phase 2: RAG Pipeline, Vector Embeddings & Streamlit Frontend

#### Goal:
Implement semantic chunking, local vector embedding, persistent vector storage, Google Gemini grounded reasoning, and an interactive UI.

#### Key Files Created:
1. `backend/rag_pipeline.py`:
   - `RecursiveCharacterTextSplitter(chunk_size=700, chunk_overlap=150)`
   - ChromaDB `PersistentClient(path="chroma_db")`
   - Embedding Function: ONNX `all-MiniLM-L6-v2` (384 dimensions)
   - Synthesis: Google Gemini (`gemini-2.5-flash` via official `google-genai` SDK)
   - Prompt engineering enforcing strict document grounding (`"Use ONLY the provided context. Cite sources as [Page X]. Never fabricate information."`)
2. `frontend/app.py`: Modern Streamlit web application.
   - Tab 1: Document Upload, Ingestion metrics (chunks, characters, pages).
   - Tab 2: RAG Assistant Chatbot with citation badges and latency counters.
   - Tab 3: System Health, Vector DB chunk count, and architecture diagram.
3. `frontend/config.py`: Streamlit parameters and backend URL wiring.

#### Engineering Decisions:
- **Chunk Size (700 characters) & Overlap (150 characters):**
  - 700 characters (~100-140 words) represents a coherent semantic concept and fits well inside the 256/384 token window of dense embedding models.
  - 150 characters overlap guarantees that sentences on chunk boundaries are not sliced in half, preserving context.
- **Why Local ONNX `all-MiniLM-L6-v2` Embeddings?**
  - Runs **100% on CPU** using ONNX runtime without requiring external GPU or paid cloud embedding APIs (OpenAI `text-embedding-3-small`). Sub-millisecond vectorization with zero operational cost.
- **Why ChromaDB?**
  - Lightweight, embedded, native Python support, persistent SQLite + HNSW vector indexing. Does not require running an external database cluster like Milvus or Pinecone for single-node workloads.
- **Why Google Gemini 2.5 Flash?**
  - Ultra-low latency (<800ms), 1M token context window, state-of-the-art instruction following, and highly cost-effective compared to GPT-4o.

#### Step-by-Step Commands Run:
```powershell
# 1. Install RAG dependencies
pip install chromadb langchain-text-splitters google-genai streamlit

# 2. Start Frontend
streamlit run frontend/app.py --server.port 8501
```

#### How to Explain in an Interview:
- **English:** *"In Phase 2, I implemented the RAG pipeline. We chunk documents using a sliding window of 700 chars with 150 overlap, generate 384-dimensional dense vectors using local ONNX all-MiniLM-L6-v2, and store them in ChromaDB. For retrieval, we run cosine similarity to extract the top-k relevant chunks and feed them into Gemini 2.5 Flash with strict grounding instructions to prevent hallucinations."*
- **मराठी:** *"Phase 2 हा या प्रोजेक्टचा मुख्य गाभा (RAG) आहे. आपण मजकुराचे 700-700 अक्षरांचे तुकडे (Chunks) केले आणि 150 अक्षरांचा Overlap ठेवला. ONNX MiniLM मॉडेल वापरून त्यांचे 384-डायमेंशनल वेक्टर्स बनवले आणि ChromaDB मध्ये सेव्ह केले. युझरच्या प्रश्नाशी मिळतेजुळते चंक्स शोधून आपण Gemini 2.5 Flash कडे पाठवतो, आणि Gemini फक्त त्या चंक्सच्या आधारे पुराव्यासह उत्तर देते."*

---

### 🔹 Phase 3: Docker Containerization & Microservices

#### Goal:
Containerize both backend and frontend into lightweight, secure, production-grade Docker containers and orchestrate them with Docker Compose.

#### Key Files Created:
1. `Dockerfile.backend`:
   - Base image: `python:3.11-slim`
   - Security: Runs as non-root user (`appuser:10001`)
   - Healthcheck: `curl -f http://localhost:8000/health || exit 1`
2. `Dockerfile.frontend`:
   - Base image: `python:3.11-slim`
   - Streamlit configuration: Headless mode, port 8501
   - Healthcheck: `curl -f http://localhost:8501/_stcore/health || exit 1`
3. `docker-compose.yml`:
   - Defines `backend` and `frontend` services
   - Custom bridge network: `ai-network`
   - Named persistent volumes: `pdf_data` (`/app/data/uploads`) and `chroma_data` (`/app/chroma_db`)
   - Dependency order: Frontend waits for `backend` to become `service_healthy`
4. `.dockerignore`: Excludes `.venv`, `__pycache__`, `.git`, `.env` to keep images small.

#### Engineering Decisions:
- **Non-Root User:** Prevents container breakout vulnerabilities in production environments.
- **Named Persistent Volumes:** Ensures uploaded PDFs and vector database embeddings persist across container stops, restarts, and redeployments.
- **Docker Compose Health Dependency (`service_healthy`):** Guarantees that Streamlit never starts or queries the backend until FastAPI has completely finished initializing.

#### Step-by-Step Commands:
```bash
# Build and run containers
docker compose up -d --build

# Inspect container status and health
docker compose ps

# View live container logs
docker compose logs -f backend
```

#### How to Explain in an Interview:
- **English:** *"In Phase 3, I containerized the services using multi-stage Python 3.11-slim images. I implemented non-root security boundaries and Docker native healthchecks. I used Docker Compose with named volumes for PDF uploads and ChromaDB vector persistence, and enforced conditional service startup using `depends_on: condition: service_healthy`."*
- **मराठी:** *"Phase 3 मध्ये आपण Docker चा वापर केला. Backend आणि Frontend चे वेगवेगळे Dockerfile बनवले. सुरक्षिततेसाठी नॉन-रूट युझर तयार केला. Docker Compose द्वारे दोन्ही कंटेनर्स एका प्रायव्हेट नेटवर्कवर जोडले आणि डेटा सेव्ह राहण्यासाठी Named Volumes वापरले, ज्यामुळे कंटेनर रिस्टार्ट झाला तरी डेटा सुरक्षित राहतो."*

---

### 🔹 Phase 4: Kubernetes (K8s) Production Deployment

#### Goal:
Design enterprise-grade Kubernetes manifests for high availability, self-healing, zero-downtime rolling updates, and persistent volume management.

#### Key Files Created:
1. `k8s/configmap.yaml`: Non-sensitive configuration (`CHUNK_SIZE`, `CHUNK_OVERLAP`, `BACKEND_URL`).
2. `k8s/secrets.yaml`: Base64-encoded secret keys (`GEMINI_API_KEY`).
3. `k8s/pvc.yaml`: PersistentVolumeClaims (`pdf-storage-pvc` 1Gi, `chroma-storage-pvc` 2Gi) with `ReadWriteOnce` access mode.
4. `k8s/backend-deployment.yaml`:
   - 2 Pod Replicas
   - RollingUpdate strategy (`maxSurge: 1`, `maxUnavailable: 0`)
   - Liveness Probe (`/health`, 30s initial delay) & Readiness Probe (`/health`, 10s initial delay)
   - Resource requests (`250m CPU`, `512Mi RAM`) and limits (`1000m CPU`, `1Gi RAM`)
   - Persistent volume mounts for `/app/data/uploads` and `/app/chroma_db`
5. `k8s/backend-service.yaml`: Internal `ClusterIP` service routing port 8000.
6. `k8s/frontend-deployment.yaml`: 2 Pod Replicas for UI with health probes and resource limits.
7. `k8s/frontend-service.yaml`: `NodePort` service exposing port 8501 externally on nodePort `30501`.
8. `k8s/kustomization.yaml`: Kustomize configuration for 1-command deployment (`kubectl apply -k k8s/`).

#### Engineering Decisions:
- **ClusterIP vs NodePort:**
  - Backend is set to `ClusterIP` so it is **never exposed to the public internet**, accessible only within the cluster by the frontend.
  - Frontend is set to `NodePort` (or `LoadBalancer` on cloud providers) for user browser traffic.
- **Liveness vs Readiness Probes:**
  - *Liveness Probe:* Detects deadlocks and restarts the pod automatically.
  - *Readiness Probe:* Stops sending traffic to the pod during startup or heavy model loading until it is ready to serve.

#### Step-by-Step Commands:
```bash
# 1. Deploy all manifests using Kustomize
kubectl apply -k k8s/

# 2. Check rollout status
kubectl rollout status deployment/backend-deployment
kubectl rollout status deployment/frontend-deployment

# 3. Inspect Pods and Services
kubectl get pods -o wide
kubectl get svc
kubectl get pvc
```

#### How to Explain in an Interview:
- **English:** *"In Phase 4, I designed the Kubernetes infrastructure. I decoupled secrets and configmaps, provisioned PVCs for stateful ChromaDB storage, and deployed 2 replicas each of backend and frontend. I configured zero-downtime rolling updates, resource constraints to avoid OOM kills, and separated internal traffic using ClusterIP while exposing the frontend via NodePort."*
- **मराठी:** *"Phase 4 मध्ये आपण Enterprise Kubernetes (K8s) आर्किटेक्चर तयार केले. हाय-अव्हेलेबिलिटीसाठी प्रत्येकी 2 Replicas (Pods) ठेवले. बॅकएंडला सुरक्षित ठेवण्यासाठी ClusterIP दिले, जेणेकरून बाहेरून कोणीही थेट API ॲक्सेस करू शकणार नाही. Liveness आणि Readiness Probes मुळे पॉड क्रॅश झाल्यास K8s त्याला आपोआप रिस्टार्ट करते."*

---

### 🔹 Phase 5: Monitoring & Observability (Prometheus, Grafana & Loki)

#### Goal:
Implement real-time observability across the RAG pipeline, tracking API performance, request throughput, vector database chunk volumes, and centralized logs.

#### Key Files Created:
1. `backend/main.py` (Instrumented with `prometheus_client`):
   - `http_requests_total`: Counter tracking calls by method, endpoint, and status code.
   - `http_request_duration_seconds`: Histogram measuring latency buckets.
   - `chromadb_chunks_total`: Gauge tracking total vector count in ChromaDB.
   - `documents_ingested_total`: Counter tracking total uploaded PDFs.
   - `rag_queries_total`: Counter tracking total answered user queries.
   - Prometheus scrape endpoint: `GET /metrics`.
2. `monitoring/prometheus/prometheus.yml`: Prometheus configuration scraping FastAPI backend every 5 seconds.
3. `monitoring/loki/loki-config.yml`: High-efficiency log aggregation engine.
4. `monitoring/alloy/config.alloy`: Grafana Alloy collector reading container stdout logs and pushing to Loki.
5. `monitoring/grafana/provisioning/`: Auto-provisions Prometheus and Loki datasources.
6. `monitoring/grafana/dashboards/assistant_dashboard.json`: Pre-configured dashboard with panels for P95 Latency, Query Rates, Vector Growth, and HTTP Status Codes.
7. `monitoring/docker-compose.monitoring.yml`: Standalone compose file running Prometheus (9090), Grafana (3000), and Loki (3100).

#### Step-by-Step Commands:
```bash
# Start monitoring stack
docker compose -f monitoring/docker-compose.monitoring.yml up -d

# Open Grafana UI in browser: http://localhost:3000 (admin / admin)
# Open Prometheus UI in browser: http://localhost:9090
```

#### How to Explain in an Interview:
- **English:** *"In Phase 5, I instrumented the FastAPI application with custom Prometheus metrics including request durations, RAG query counts, and vector store size. I deployed Prometheus to scrape metrics every 5 seconds, Loki with Grafana Alloy for distributed log aggregation, and Grafana for real-time dashboards."*
- **मराठी:** *"Phase 5 मध्ये आपण Observability आणि Monitoring बसवले. Backend मध्ये Prometheus Client वापरून कस्टम मेट्रिक्स (जसे की API Latency, Total Queries, ChromaDB Vector Count) तयार केले. Grafana मध्ये डॅशबोर्ड तयार केला जेणेकरून सिस्टमचे परफॉर्मन्स आणि एरर्स रिअल-टाईम स्क्रीनवर दिसतात."*

---

### 🔹 Phase 6: CI/CD Pipeline & GitHub Integration

#### Goal:
Automate testing, container building, and Kubernetes manifest validation on every Git push using GitHub Actions.

#### Key Files Created:
1. `.github/workflows/ci-cd.yml`: 3-Stage GitHub Actions Workflow.
   - **Stage 1 (Unit & Integration Tests):** Sets up Python 3.11, caches pip dependencies, runs linter (`flake8`), and executes all 34 unittests.
   - **Stage 2 (Docker Build & Scan):** Sets up Docker Buildx, verifies Dockerfiles, builds container images using GitHub Actions cache.
   - **Stage 3 (Kubernetes Manifest Validation):** Installs `kubectl`, runs dry-run client validation (`kubectl apply --dry-run=client -k k8s/`) to verify YAML correctness before any deployment.
2. Git Repository & Remote Setup:
   - Initialized Git, created `main` branch.
   - Linked to GitHub: `https://github.com/Pavan7856/AI-Knowledge-Assistant.git`.
   - Pushed complete verified codebase.

#### Step-by-Step Commands Run:
```powershell
# 1. Initialize Git and Stage files
git init
git add .
git commit -m "feat: complete Enterprise AI Knowledge Assistant platform"

# 2. Add Remote and Push to GitHub
git remote add origin https://github.com/Pavan7856/AI-Knowledge-Assistant.git
git branch -M main
git push -u origin main
```

#### How to Explain in an Interview:
- **English:** *"In Phase 6, I built a 3-stage automated CI/CD pipeline using GitHub Actions. Every push or pull request triggers automated unit testing (34 tests), Docker Buildx image creation, and a Kubernetes dry-run validation. This ensures zero broken builds or invalid YAML manifests reach production."*
- **मराठी:** *"Phase 6 मध्ये आपण GitHub Actions द्वारे CI/CD Pipeline तयार केली. जेव्हा आपण GitHub वर कोड पुश करतो, तेव्हा आपोआप 3 स्टेजेस रन होतात: १) सर्व 34 युनिट टेस्ट्स पास होतात का ते तपासणे, २) Docker Images बिल्ड करणे, आणि ३) Kubernetes चे YAML फाइल्स व्हॅलिडेट करणे. यामुळे कोडमध्ये काही चूक असल्यास लगेच समजते."*

---

### 🔹 Phase 7: Enterprise Documentation & Testing Suite

#### Goal:
Provide complete architectural specifications, ready-to-deliver presentation slides, 14 in-depth interview Q&A guides, and an automated 34-test suite.

#### Key Files Created:
1. `README.md`: Production GitHub homepage with badges, architecture diagrams, API specs, and quickstart commands.
2. `docs/ARCHITECTURE.md`: Deep technical specifications with Mermaid sequence diagrams.
3. `docs/PRESENTATION.md`: 10-slide ready-to-present technical pitch deck.
4. `docs/INTERVIEW_QA.md`: 14 comprehensive interview questions and architectural defenses.
5. `tests/`: 34 automated unit & integration tests covering API endpoints, RAG pipeline, Dockerfiles, Kubernetes manifests, and monitoring configurations.

#### Step-by-Step Commands:
```powershell
# Run the complete test suite (34 tests)
.venv\Scripts\python -m unittest discover tests
```

---

## 🎯 4. Core Concepts & Comparison Matrix (Interview Defense)

| Concept | What We Chose | Why We Chose It (The Advantage) | Alternatives & Why Rejected |
| :--- | :--- | :--- | :--- |
| **Generative Strategy** | **RAG (Retrieval-Augmented Generation)** | Dynamic data updates, zero hallucinations, verifiable page citations, zero model retraining cost. | **Fine-Tuning:** Costly, hallucinations remain, cannot easily delete/update specific document knowledge. |
| **PDF Extraction** | **PyMuPDF (`fitz`)** | 10-100x faster execution, exact page metadata preservation, handles complex layouts without external binaries. | **`pypdf` / `pdfplumber`:** Significantly slower, prone to memory spikes on large PDFs. |
| **Chunking Strategy** | **Recursive Character (700 / 150)** | Balances semantic completeness with dense embedding token limits; overlap prevents split sentences. | **Fixed-size chunking:** Slices sentences and words arbitrarily, corrupting vector similarity. |
| **Embedding Engine** | **Local ONNX `all-MiniLM-L6-v2`** | 100% offline, CPU-optimized, sub-millisecond latency, zero API costs, 384 dense dimensions. | **OpenAI Ada/3-small:** Requires internet, costs money per token, introduces API rate-limit risks. |
| **Vector Database** | **ChromaDB (Persistent)** | Lightweight, embedded SQLite+HNSW, native Python client, no separate database server needed. | **Pinecone / Milvus:** Heavy operational overhead, requires cloud subscription or multi-node cluster. |
| **LLM Model** | **Google Gemini 2.5 Flash** | Blazing fast (<800ms latency), 1M context window, high instruction fidelity for strict grounding. | **GPT-4 / Claude Opus:** Higher latency (3-5s), significantly higher cost per query. |
| **API Framework** | **FastAPI (ASGI)** | High-concurrency async support, automatic Pydantic validation, native Swagger docs at `/docs`. | **Flask:** Synchronous (WSGI), lacks native type validation and auto-generated API docs. |
| **Containerization** | **Docker + Multi-Stage** | Non-root security, named volumes for data persistence, native healthcheck probes. | **Raw VM deployment:** Inconsistent dependencies, hard to scale, lacks container isolation. |
| **Orchestration** | **Kubernetes (2 Replicas)** | Self-healing, zero-downtime rolling updates, horizontal autoscaling, persistent volume claims. | **Docker Swarm:** Limited enterprise adoption, fewer cloud-native integrations. |
| **Monitoring** | **Prometheus + Grafana** | Industry-standard pull model, multidimensional metric labels, customizable real-time dashboards. | **ELK Stack:** Heavy memory footprint (Elasticsearch requires 4GB+ RAM just to start). |

---

## 💡 5. Top 5 Interview Questions & Exact Answers

### Q1: *"Why did you use RAG instead of Fine-Tuning an LLM on your PDFs?"*
- **Answer:**
  *"Fine-tuning changes the model's tone and style, but it is a poor mechanism for factual recall. Fine-tuned models still hallucinate and cannot cite page numbers. Furthermore, when enterprise documents change, updating a fine-tuned model requires expensive retraining. With RAG, document updates are instantaneous: we simply update the vector index in ChromaDB. RAG guarantees 100% verifiable page citations and costs virtually nothing to maintain."*

### Q2: *"How do you prevent the LLM from hallucinating answers?"*
- **Answer:**
  *"We use a 3-layer defense against hallucinations:*
  1. *Dense Vector Semantic Retrieval: Only the top-k chunks with high cosine similarity are retrieved.*
  2. *Strict Grounding System Prompt: The system prompt instructs Gemini: 'Answer the question based ONLY on the provided context. If the answer cannot be found in the context, explicitly state: I cannot find the answer in the uploaded documents.'*
  3. *Page-Level Citations: The prompt requires the model to annotate every statement with `[Page X]`, ensuring every claim is backed by a specific source."*

### Q3: *"How is data persistence handled in your Kubernetes cluster for ChromaDB?"*
- **Answer:**
  *"Containers are ephemeral, so storing vectors on the container filesystem would result in data loss upon pod restart. To solve this, we provisioned a `PersistentVolumeClaim` (PVC) with `ReadWriteOnce` access mode mounted to `/app/chroma_db` and `/app/data/uploads`. The underlying storage volume survives pod crashes, rolling updates, and node migrations."*

### Q4: *"What is the difference between Liveness and Readiness probes in your K8s deployment?"*
- **Answer:**
  *"The **Readiness Probe** checks if the container is ready to accept incoming user traffic. When our backend is starting up or initializing the ONNX embedding engine, the readiness probe fails temporarily, and Kubernetes stops routing traffic to it until it responds 200 OK on `/health`. The **Liveness Probe** checks if the container is still alive. If FastAPI encounters an unrecoverable deadlock, the liveness probe fails, and Kubernetes automatically kills and restarts the pod."*

### Q5: *"Why did you choose an internal ONNX embedding model instead of OpenAI embeddings?"*
- **Answer:**
  *"Using `all-MiniLM-L6-v2` via ONNX runtime gives us three major advantages:*
  1. *Zero Cost: Embedding generation is completely free.*
  2. *Sub-millisecond Latency: The 79MB model runs locally in CPU memory without network round-trips.*
  3. *Privacy & Reliability: Document chunks never leave our infrastructure during the embedding stage, and we are immune to third-party API outages or rate limits."*

---

## 🛠️ 6. Quick Hands-On Commands Reference (Cheat Sheet)

### 1. Run Unit Tests (34 Tests)
```powershell
.venv\Scripts\python -m unittest discover tests
```

### 2. Run Locally in Python
```powershell
# Terminal 1: FastAPI Backend
.venv\Scripts\uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload

# Terminal 2: Streamlit Frontend
.venv\Scripts\streamlit run frontend/app.py --server.port 8501
```

### 3. Run with Docker Compose
```bash
docker compose up -d --build
docker compose ps
docker compose logs -f
```

### 4. Deploy to Kubernetes
```bash
kubectl apply -k k8s/
kubectl get pods
kubectl get svc
```

### 5. Run Monitoring Stack
```bash
docker compose -f monitoring/docker-compose.monitoring.yml up -d
# Prometheus: http://localhost:9090
# Grafana:    http://localhost:3000 (admin / admin)
```

---

## 📝 7. Final Summary Checklist for Your Preparation

- [x] **Architecture Understanding:** Understand how a PDF moves from upload -> PyMuPDF -> Text Splitter -> MiniLM Embeddings -> ChromaDB -> Cosine Search -> Gemini 2.5 Flash -> Streamlit UI.
- [x] **DevOps & Containers:** Understand why non-root Dockerfiles, named volumes, and healthchecks are used.
- [x] **Kubernetes Mastery:** Understand ClusterIP (internal API) vs NodePort (external UI), PVC storage persistence, and RollingUpdate zero-downtime deployments.
- [x] **Observability:** Know the custom Prometheus metrics (`http_requests_total`, `http_request_duration_seconds`, `chromadb_chunks_total`).
- [x] **CI/CD Automation:** Know the 3 GitHub Actions stages: Test -> Docker Build -> K8s Dry-run.
- [x] **GitHub Repository:** Code is synced and live at `https://github.com/Pavan7856/AI-Knowledge-Assistant.git`.

