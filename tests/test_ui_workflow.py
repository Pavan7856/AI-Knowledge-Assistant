import unittest
from pathlib import Path
import io
import pymupdf
from fastapi.testclient import TestClient

from backend.main import app
from backend.config import UPLOAD_DIR

class TestUIWorkflow(unittest.TestCase):
    """
    Complete End-to-End User Interface and API Workflow Test (100% English):
    - Health & Status Checks
    - PDF Document Ingestion & Chunking
    - Vector Embedding Indexing
    - Context Retrieval & Citation verification
    - Knowledge Base Reset
    """

    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)
        cls.sample_pdf_name = "Enterprise_Cloud_Architecture.pdf"
        cls.sample_pdf_path = UPLOAD_DIR / cls.sample_pdf_name

        # Create realistic 2-page document
        doc = pymupdf.open()
        
        # Page 1: Cloud Microservices
        p1 = doc.new_page()
        p1.insert_text(
            (50, 72),
            "Enterprise Cloud Architecture - Chapter 1: Microservices.\n"
            "Microservices architecture structures an application as a collection of loosely coupled services.\n"
            "Each microservice is fine-grained and protocols are lightweight, commonly using HTTP REST or gRPC.\n"
            "Independent deployability is the primary benefit of microservices."
        )

        # Page 2: Vector Search & Embeddings
        p2 = doc.new_page()
        p2.insert_text(
            (50, 72),
            "Enterprise Cloud Architecture - Chapter 2: Vector Search & AI.\n"
            "Vector databases index high-dimensional embeddings to perform semantic search.\n"
            "ChromaDB stores document embeddings and computes cosine similarity for retrieval.\n"
            "This enables Retrieval-Augmented Generation (RAG) to feed precise context to LLMs."
        )

        doc.save(cls.sample_pdf_path)
        doc.close()

    @classmethod
    def tearDownClass(cls):
        if cls.sample_pdf_path.exists():
            cls.sample_pdf_path.unlink()
        cls.client.post("/api/reset-database")

    def test_01_backend_health_status(self):
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "healthy")
        self.assertEqual(data["service"], "backend-api")
        print("\n[UI Workflow Test 1/5] Backend health check verified.")

    def test_02_pdf_upload_and_vector_indexing(self):
        with open(self.sample_pdf_path, "rb") as f:
            pdf_bytes = f.read()

        files = {"file": (self.sample_pdf_name, io.BytesIO(pdf_bytes), "application/pdf")}
        response = self.client.post("/api/upload-pdf", files=files)
        self.assertEqual(response.status_code, 200)
        data = response.json()

        self.assertEqual(data["file_name"], self.sample_pdf_name)
        self.assertEqual(data["total_pages"], 2)
        self.assertGreater(data["total_chars"], 100)
        self.assertGreaterEqual(data["chunks_indexed"], 2)
        print(f"[UI Workflow Test 2/5] PDF uploaded and {data['chunks_indexed']} chunks indexed in ChromaDB.")

    def test_03_query_page_1_retrieval(self):
        query_payload = {
            "question": "What is the primary benefit of microservices architecture?",
            "top_k": 2
        }
        response = self.client.post("/api/query", json=query_payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()

        self.assertIn("answer", data)
        self.assertGreater(len(data["sources"]), 0)
        top_source = data["sources"][0]
        self.assertEqual(top_source["page"], 1, "Expected citation to point to Page 1")
        self.assertEqual(top_source["source"], self.sample_pdf_name)
        print("[UI Workflow Test 3/5] Query retrieved Page 1 microservices citation with high precision.")

    def test_04_query_page_2_retrieval(self):
        query_payload = {
            "question": "How does ChromaDB enable Retrieval-Augmented Generation?",
            "top_k": 2
        }
        response = self.client.post("/api/query", json=query_payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()

        self.assertIn("answer", data)
        self.assertGreater(len(data["sources"]), 0)
        top_source = data["sources"][0]
        self.assertEqual(top_source["page"], 2, "Expected citation to point to Page 2")
        self.assertIn("chromadb", top_source["snippet"].lower())
        print("[UI Workflow Test 4/5] Query retrieved Page 2 ChromaDB citation with high precision.")

    def test_05_database_reset_flow(self):
        response = self.client.post("/api/reset-database")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["total_docs"], 0)
        print("[UI Workflow Test 5/5] Vector database reset verified successfully.")

if __name__ == "__main__":
    unittest.main()

