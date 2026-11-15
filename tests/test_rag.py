import unittest
from pathlib import Path
import os
import pymupdf

from backend.pdf_processor import PDFProcessor
from backend.rag_pipeline import RAGPipeline
from backend.config import UPLOAD_DIR, CHROMA_DIR

class TestPhase2RAG(unittest.TestCase):
    """
    Test suite for Phase 2 RAG Pipeline:
    1. Text chunking and page metadata tracking
    2. Embedding creation and ChromaDB indexing
    3. Similarity search and context retrieval accuracy
    4. Citations & Page References
    """

    def setUp(self):
        # Create a specialized multi-topic PDF for testing retrieval
        self.test_pdf = UPLOAD_DIR / "rag_evaluation_guide.pdf"
        doc = pymupdf.open()

        # Page 1: Topic - Python Data Structures
        p1 = doc.new_page()
        p1.insert_text(
            (50, 72),
            "Topic: Python Data Structures.\n"
            "In Python, a list is mutable, which means its elements can be modified, appended, or removed after creation.\n"
            "On the other hand, a tuple is immutable, meaning once created, elements cannot be altered or deleted.\n"
            "Tuples are generally faster and memory-efficient compared to lists."
        )

        # Page 2: Topic - Kubernetes Architecture
        p2 = doc.new_page()
        p2.insert_text(
            (50, 72),
            "Topic: Kubernetes Architecture.\n"
            "Kubernetes is an open-source container orchestration system.\n"
            "The Control Plane consists of the API Server, etcd storage, Controller Manager, and Scheduler.\n"
            "Worker nodes host application Pods and run kubelet and kube-proxy."
        )

        doc.save(self.test_pdf)
        doc.close()

        # Test RAG Pipeline instance with test collection
        self.rag = RAGPipeline(collection_name="test_rag_collection")

    def tearDown(self):
        # Cleanup PDF
        if self.test_pdf.exists():
            self.test_pdf.unlink()
        # Reset test collection
        try:
            self.rag.reset_collection()
        except Exception:
            pass

    def test_end_to_end_rag_ingestion_and_retrieval(self):
        # 1. Extract text from PDF
        extraction = PDFProcessor.extract_text_from_pdf(self.test_pdf)
        self.assertEqual(extraction["total_pages"], 2)

        # 2. Ingest into ChromaDB
        ingest_stats = self.rag.ingest_pdf_content(self.test_pdf.name, extraction["pages"])
        self.assertGreaterEqual(ingest_stats["total_chunks_created"], 2)
        print(f"\n[SUCCESS] Ingested {ingest_stats['total_chunks_created']} chunks into ChromaDB!")

        # 3. Query Topic 1: List vs Tuple (Expected: Page 1)
        res1 = self.rag.query("What is the difference between list and tuple?", top_k=1)
        self.assertGreater(len(res1["sources"]), 0)
        top_source_1 = res1["sources"][0]
        self.assertEqual(top_source_1["page"], 1, "Expected Page 1 for list vs tuple query")
        self.assertIn("mutable", top_source_1["snippet"].lower())
        print("[SUCCESS] Query 1 correctly retrieved Page 1 for Python Data Structures!")

        # 4. Query Topic 2: Kubernetes Control Plane (Expected: Page 2)
        res2 = self.rag.query("What are the components of Kubernetes Control Plane?", top_k=1)
        self.assertGreater(len(res2["sources"]), 0)
        top_source_2 = res2["sources"][0]
        self.assertEqual(top_source_2["page"], 2, "Expected Page 2 for Kubernetes query")
        self.assertIn("control plane", top_source_2["snippet"].lower())
        print("[SUCCESS] Query 2 correctly retrieved Page 2 for Kubernetes Architecture!")

if __name__ == "__main__":
    unittest.main()

