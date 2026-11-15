import pymupdf
from pathlib import Path
from typing import Dict, Any, List

class PDFProcessor:
    """
    Handles PDF text extraction and document parsing using PyMuPDF.
    """

    @staticmethod
    def extract_text_from_pdf(file_path: Path) -> Dict[str, Any]:
        """
        Reads a PDF file and extracts text page by page.
        Returns document metadata and content.
        """
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        doc = pymupdf.open(file_path)
        pages_content: List[Dict[str, Any]] = []
        full_text_list: List[str] = []

        for page_num in range(len(doc)):
            page = doc[page_num]
            text = page.get_text("text").strip()
            pages_content.append({
                "page_number": page_num + 1,
                "text": text,
                "char_count": len(text)
            })
            if text:
                full_text_list.append(text)

        total_pages = len(doc)
        total_chars = sum(p["char_count"] for p in pages_content)
        full_text = "\n\n".join(full_text_list)
        doc.close()

        return {
            "file_name": file_path.name,
            "total_pages": total_pages,
            "total_chars": total_chars,
            "pages": pages_content,
            "preview": full_text[:1000] if full_text else "",
            "is_scanned": total_chars == 0 and total_pages > 0
        }

