import unittest
from pathlib import Path
import pymupdf
import io
import asyncio
from fastapi import UploadFile

from backend.main import app, health_check, root, upload_pdf, list_documents
from backend.pdf_processor import PDFProcessor
from backend.config import UPLOAD_DIR

class TestPhase1(unittest.TestCase):
    """
    Direct Unit Test suite for Phase 1:
    1. PDF text extraction with PyMuPDF
    2. FastAPI Endpoint Logic (Health, Root, Upload, List)
    Runs completely in-memory in milliseconds!
    """

    def setUp(self):
        self.test_pdf_path = UPLOAD_DIR / "sample_test.pdf"
        
        # Create a small test PDF
        doc = pymupdf.open()
        page1 = doc.new_page()
        page1.insert_text((50, 72), "Welcome to Enterprise AI Knowledge Assistant.\nThis is Page 1.")
        page2 = doc.new_page()
        page2.insert_text((50, 72), "This is Page 2 of the sample test document.\nTesting PyMuPDF extraction.")
        doc.save(self.test_pdf_path)
        doc.close()

    def tearDown(self):
        if self.test_pdf_path.exists():
            self.test_pdf_path.unlink()

    def test_pdf_extraction(self):
        result = PDFProcessor.extract_text_from_pdf(self.test_pdf_path)
        self.assertEqual(result["total_pages"], 2)
        self.assertGreater(result["total_chars"], 50)
        self.assertIn("Enterprise AI Knowledge Assistant", result["preview"])
        self.assertFalse(result["is_scanned"])
        self.assertEqual(len(result["pages"]), 2)
        print("\n[SUCCESS] PDFProcessor text extraction passed!")

    def test_fastapi_health(self):
        result = health_check()
        self.assertEqual(result["status"], "healthy")
        print("\n[SUCCESS] FastAPI /health logic passed!")

    def test_fastapi_root(self):
        result = root()
        self.assertIn("message", result)
        self.assertEqual(result["docs_url"], "/docs")
        print("\n[SUCCESS] FastAPI / (root) endpoint passed!")

    def test_fastapi_upload_logic(self):
        # Create dummy PDF bytes
        doc = pymupdf.open()
        p = doc.new_page()
        p.insert_text((50, 72), "API Upload Test Document for Knowledge Assistant.")
        pdf_bytes = doc.tobytes()
        doc.close()

        upload_file_obj = UploadFile(
            filename="unit_test_doc.pdf",
            file=io.BytesIO(pdf_bytes)
        )

        result = asyncio.run(upload_pdf(upload_file_obj))
        self.assertEqual(result["file_name"], "unit_test_doc.pdf")
        self.assertEqual(result["total_pages"], 1)
        self.assertIn("API Upload Test Document", result["preview"])
        print("\n[SUCCESS] FastAPI upload_pdf logic passed!")

        # Cleanup uploaded test file
        test_file = UPLOAD_DIR / "unit_test_doc.pdf"
        if test_file.exists():
            test_file.unlink()

    def test_list_documents(self):
        result = list_documents()
        self.assertIn("documents", result)
        print("\n[SUCCESS] FastAPI list_documents endpoint passed!")

if __name__ == "__main__":
    unittest.main()
