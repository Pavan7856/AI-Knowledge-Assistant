from fastapi import FastAPI, UploadFile, File, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from pydantic import BaseModel, Field
from pathlib import Path
from typing import Optional
import shutil
import os
import time
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST

from backend.config import UPLOAD_DIR, ALLOWED_EXTENSIONS
from backend.pdf_processor import PDFProcessor
from backend.rag_pipeline import RAGPipeline

app = FastAPI(
    title="Mini Enterprise AI Knowledge Assistant - Backend API",
    description="FastAPI Backend with PyMuPDF, ChromaDB Vector Search, Gemini RAG, and Prometheus Metrics",
    version="2.1.0"
)

# CORS middleware for Streamlit frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global RAG Pipeline Instance
rag_pipeline = RAGPipeline()

# ==========================================
# Prometheus Metrics Instrumentation
# ==========================================
REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total HTTP Requests Processed",
    ["method", "endpoint", "status_code"]
)
REQUEST_LATENCY = Histogram(
    "http_request_duration_seconds",
    "HTTP Request Latency in Seconds",
    ["endpoint"]
)
DOCS_INGESTED = Counter(
    "documents_ingested_total",
    "Total PDF Documents Ingested"
)
CHROMA_CHUNKS_GAUGE = Gauge(
    "chromadb_chunks_total",
    "Total Vector Chunks Stored in ChromaDB"
)
RAG_QUERIES_COUNT = Counter(
    "rag_queries_total",
    "Total RAG Search Queries Executed"
)

@app.middleware("http")
async def prometheus_metrics_middleware(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time

    endpoint = request.url.path
    # Exclude metrics endpoint from tracking noise
    if endpoint != "/metrics":
        REQUEST_COUNT.labels(
            method=request.method,
            endpoint=endpoint,
            status_code=response.status_code
        ).inc()
        REQUEST_LATENCY.labels(endpoint=endpoint).observe(duration)

    return response

# Pydantic Schemas
class QueryRequest(BaseModel):
    question: str = Field(..., description="User question to search in knowledge base")
    top_k: int = Field(3, ge=1, le=10, description="Number of context chunks to retrieve")

class ApiKeyRequest(BaseModel):
    api_key: str = Field(..., description="Google Gemini API Key")

@app.get("/")
def root():
    return {
        "message": "Welcome to Mini Enterprise AI Knowledge Assistant API",
        "docs_url": "/docs",
        "health": "/health",
        "metrics": "/metrics",
        "phase": "Phase 5 (Monitoring & Observability)"
    }

@app.get("/health")
def health_check():
    count = rag_pipeline.collection.count()
    CHROMA_CHUNKS_GAUGE.set(count)
    return {
        "status": "healthy",
        "service": "backend-api",
        "vector_db": "ChromaDB Active",
        "total_vectors": count,
        "llm_connected": rag_pipeline.llm_initialized
    }

@app.get("/metrics")
def metrics():
    """
    Exposes application metrics for Prometheus scraping.
    """
    CHROMA_CHUNKS_GAUGE.set(rag_pipeline.collection.count())
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)

@app.post("/api/upload-pdf")
async def upload_pdf(file: UploadFile = File(...)):
    """
    1. Validates and saves PDF to data/uploads
    2. Extracts text page-by-page using PyMuPDF
    3. Chunks text and generates vector embeddings in ChromaDB
    """
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type '{file_ext}'. Only PDF files are allowed."
        )

    destination = UPLOAD_DIR / file.filename

    # Save uploaded file
    try:
        with destination.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")

    # Extract text with PyMuPDF
    try:
        extraction_result = PDFProcessor.extract_text_from_pdf(destination)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to extract text: {str(e)}")

    # Ingest into ChromaDB RAG Pipeline
    try:
        rag_result = rag_pipeline.ingest_pdf_content(
            file_name=file.filename,
            pages=extraction_result["pages"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to index into ChromaDB: {str(e)}")

    # Update metrics
    DOCS_INGESTED.inc()
    CHROMA_CHUNKS_GAUGE.set(rag_result["total_docs_in_collection"])

    file_size_kb = round(destination.stat().st_size / 1024, 2)

    return {
        "message": "File uploaded, extracted, and indexed in ChromaDB successfully!",
        "file_name": file.filename,
        "file_size_kb": file_size_kb,
        "total_pages": extraction_result["total_pages"],
        "total_chars": extraction_result["total_chars"],
        "is_scanned": extraction_result["is_scanned"],
        "chunks_indexed": rag_result["total_chunks_created"],
        "total_knowledge_base_chunks": rag_result["total_docs_in_collection"],
        "preview": extraction_result["preview"]
    }

@app.post("/api/query")
def query_knowledge_base(request: QueryRequest):
    """
    Retrieves most similar document chunks from ChromaDB and
    generates contextual answer using Google Gemini.
    """
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    try:
        result = rag_pipeline.query(
            question=request.question,
            top_k=request.top_k
        )
        RAG_QUERIES_COUNT.inc()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"RAG Query failed: {str(e)}")

@app.post("/api/set-gemini-key")
def set_gemini_key(request: ApiKeyRequest):
    """
    Update Gemini API key dynamically.
    """
    rag_pipeline.set_api_key(request.api_key)
    return {
        "status": "success",
        "llm_connected": rag_pipeline.llm_initialized
    }

@app.get("/api/documents")
def list_documents():
    """
    List all uploaded PDF documents.
    """
    files = []
    for f in UPLOAD_DIR.glob("*.pdf"):
        files.append({
            "name": f.name,
            "size_kb": round(f.stat().st_size / 1024, 2)
        })
    count = rag_pipeline.collection.count()
    CHROMA_CHUNKS_GAUGE.set(count)
    return {
        "documents": files,
        "count": len(files),
        "total_chunks_in_db": count
    }

@app.post("/api/reset-database")
def reset_database():
    """
    Clear all vector embeddings from ChromaDB.
    """
    result = rag_pipeline.reset_collection()
    CHROMA_CHUNKS_GAUGE.set(0)
    return result
