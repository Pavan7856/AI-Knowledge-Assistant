# 🏛️ System Architecture - Mini Enterprise AI Knowledge Assistant

## 1. High-Level Architectural Flowchart

```mermaid
flowchart TD
    subgraph ClientLayer["User Interface Layer"]
        User["User / Web Browser"]
        StreamlitUI["Streamlit Frontend (Port 8501)"]
    end

    subgraph APILayer["Backend & Ingestion Layer"]
        FastAPI["FastAPI REST API (Port 8000)"]
        PyMuPDF["PyMuPDF Document Parser"]
        Chunker["LangChain Recursive Chunker (700 chars / 150 overlap)"]
    end

    subgraph VectorLayer["Vector Storage & Embedding Layer"]
        LocalEmbeddings["all-MiniLM-L6-v2 ONNX Embedding Engine"]
        ChromaDB[("ChromaDB Persistent Vector Database")]
    end

    subgraph LLMLayer["Generative AI Layer"]
        GeminiLLM["Google Gemini 2.5 Flash API"]
    end

    subgraph ObservabilityLayer["Observability & Logging Stack"]
        Prometheus["Prometheus Metrics Scraper (Port 9090)"]
        Loki["Grafana Loki Log Storage (Port 3100)"]
        Alloy["Grafana Alloy Log Shipper"]
        Grafana["Grafana Dashboards (Port 3000)"]
    end

    %% User Interactions
    User -->|1. Uploads PDF Document| StreamlitUI
    User -->|2. Asks Question| StreamlitUI
    StreamlitUI -->|HTTP POST Multipart| FastAPI
    StreamlitUI -->|HTTP POST /api/query| FastAPI

    %% Ingestion Pipeline
    FastAPI -->|Extracts Text & Page Numbers| PyMuPDF
    PyMuPDF -->|Structured Pages| Chunker
    Chunker -->|Text Chunks + Metadata| LocalEmbeddings
    LocalEmbeddings -->|384-dim Dense Vectors| ChromaDB

    %% RAG Retrieval & Answer Generation
    FastAPI -->|Query Vector Search| ChromaDB
    ChromaDB -->|Top-K Context Chunks + Citations| FastAPI
    FastAPI -->|Context + Prompt + Question| GeminiLLM
    GeminiLLM -->|Grounded Answer + Page Numbers| FastAPI
    FastAPI -->|JSON Response| StreamlitUI

    %% Monitoring Pipeline
    FastAPI -.->|Exposes /metrics| Prometheus
    FastAPI -.->|Writes Logs| Alloy
    Alloy -.->|Ships Logs| Loki
    Prometheus -.->|Metrics Datasource| Grafana
    Loki -.->|Logs Datasource| Grafana
```

---

## 2. Ingestion Pipeline Breakdown

1. **Upload & Validation:**
   - PDF files uploaded via Streamlit are sent as binary streams to `POST /api/upload-pdf`.
   - The file extension is validated against `.pdf`, and size is checked.
2. **Text Extraction (`backend/pdf_processor.py`):**
   - PyMuPDF opens the PDF in memory.
   - For every page, text and metadata (page number, character counts) are captured.
   - Detects whether the PDF contains extractable text or scanned raster images.
3. **Chunking Strategy:**
   - Uses `RecursiveCharacterTextSplitter` with `chunk_size=700` and `chunk_overlap=150`.
   - Preserves semantic boundary continuity across paragraphs and sentence endings.
   - Every chunk is tagged with its origin file name, page number, and chunk index.
4. **Vector Embedding & Storage:**
   - Chunks are vectorized using the local `all-MiniLM-L6-v2` ONNX model (384-dimensional dense vectors).
   - Embeddings and metadata are indexed in `chroma_db/` with cosine distance space.

---

## 3. Query & Retrieval Pipeline (RAG)

1. **User Query:** User enters a natural language question in the Streamlit UI.
2. **Semantic Similarity Search:** ChromaDB performs approximate nearest neighbor (ANN) search and returns the top $K$ chunks (default: $K=3$).
3. **Context Assembly:** The retrieved text snippets, document names, and page numbers are concatenated into a structured context window.
4. **LLM Synthesis:** The assembled prompt is passed to Google Gemini with strict grounding instructions:
   - Use ONLY the provided document context.
   - Always state the exact page number(s).
   - If the answer is not in the context, clearly decline to hallucinate.
5. **UI Rendering:** Streamlit displays the synthesized response alongside expandable citation cards displaying document source, page number, vector similarity distance, and exact text snippets.

---

## 4. Kubernetes High-Availability Architecture

```mermaid
flowchart LR
    subgraph K8sCluster["Kubernetes Cluster (Minikube / Cloud)"]
        subgraph Ingress["Networking"]
            NodePort["frontend-service (NodePort: 30501)"]
            ClusterIP["backend-service (ClusterIP: 8000)"]
        end

        subgraph FrontendReplicas["Frontend Deployment (2 Replicas)"]
            F1["Frontend Pod 1"]
            F2["Frontend Pod 2"]
        end

        subgraph BackendReplicas["Backend Deployment (2 Replicas)"]
            B1["Backend Pod 1"]
            B2["Backend Pod 2"]
        end

        subgraph PersistentVolumes["Storage (PVCs)"]
            PVC1[("pdf-storage-pvc (1Gi)")]
            PVC2[("chroma-storage-pvc (2Gi)")]
        end
    end

    UserBrowser["Browser"] --> NodePort
    NodePort --> F1 & F2
    F1 & F2 --> ClusterIP
    ClusterIP --> B1 & B2
    B1 & B2 --> PVC1 & PVC2
```

---

## 5. Security & Reliability Highlights

* **Decoupled Architecture:** Frontend and Backend run as independent services and can scale independently.
* **Resilience:** Liveness and readiness probes guarantee self-healing if a container encounters an unhandled exception.
* **Data Persistence:** Persistent Volume Claims (PVC) prevent data loss during pod restarts or node rescheduling.
* **Zero Vendor Lock-in for Embeddings:** Embeddings run completely locally using open-source ONNX models.
