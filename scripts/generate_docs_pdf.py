"""
Enterprise AI Knowledge Assistant - Documentation to PDF Converter.
Converts all project markdown documentation files into professionally formatted PDF documents using PyMuPDF.
"""

import os
import pymupdf
from markdown_it import MarkdownIt

CSS_STYLING = """
body { font-family: sans-serif; font-size: 10pt; color: #1e293b; line-height: 1.5; }
h1 { font-size: 18pt; color: #1e40af; border-bottom: 2px solid #3b82f6; padding-bottom: 4px; margin-top: 20px; }
h2 { font-size: 13pt; color: #1e3a8a; margin-top: 16px; border-bottom: 1px solid #e2e8f0; padding-bottom: 3px; }
h3 { font-size: 11pt; color: #0284c7; margin-top: 12px; }
table { border-collapse: collapse; width: 100%; margin: 12px 0; }
th, td { border: 1px solid #cbd5e1; padding: 6px 8px; font-size: 8.5pt; text-align: left; }
th { background-color: #f1f5f9; font-weight: bold; color: #0f172a; }
tr:nth-child(even) { background-color: #f8fafc; }
pre { background-color: #f1f5f9; border: 1px solid #cbd5e1; border-radius: 4px; padding: 8px; font-family: monospace; font-size: 8pt; white-space: pre-wrap; word-break: break-all; margin: 8px 0; }
code { font-family: monospace; background-color: #f1f5f9; padding: 2px 4px; border-radius: 3px; font-size: 8.5pt; }
blockquote { border-left: 3px solid #3b82f6; margin: 8px 0; padding: 6px 12px; background-color: #eff6ff; color: #1e40af; font-style: italic; }
ul, ol { margin: 8px 0; padding-left: 20px; }
li { margin-bottom: 4px; }
p { margin: 6px 0; }
"""

DOCS_MAP = {
    "docs/STEP_BY_STEP_PREPARATION_GUIDE.md": "docs/STEP_BY_STEP_PREPARATION_GUIDE.pdf",
    "docs/RUN_AND_DEPLOYMENT_GUIDE.md": "docs/RUN_AND_DEPLOYMENT_GUIDE.pdf",
    "docs/INTERVIEW_QA.md": "docs/INTERVIEW_QA.pdf",
    "docs/PRESENTATION.md": "docs/PRESENTATION.pdf",
    "docs/ARCHITECTURE.md": "docs/ARCHITECTURE.pdf",
    "README.md": "docs/README.pdf",
}

def convert_md_to_pdf(md_path: str, pdf_path: str) -> int:
    if not os.path.exists(md_path):
        print(f"[SKIP] {md_path} does not exist.")
        return 0

    with open(md_path, "r", encoding="utf-8") as f:
        text = f.read()

    md = MarkdownIt().enable("table")
    html = md.render(text)

    writer = pymupdf.DocumentWriter(pdf_path)
    story = pymupdf.Story(html=html, user_css=CSS_STYLING)

    def rectfn(rect_num, filled):
        mediabox = pymupdf.Rect(0, 0, 595, 842) # A4 Size
        rect = pymupdf.Rect(40, 45, 555, 797)
        return mediabox, rect, pymupdf.Matrix()

    story.write(writer, rectfn)
    writer.close()

    doc = pymupdf.open(pdf_path)
    page_count = len(doc)
    doc.close()
    print(f"[SUCCESS] {pdf_path} ({page_count} pages)")
    return page_count

if __name__ == "__main__":
    print("Generating PDF documentation...")
    for md_file, pdf_file in DOCS_MAP.items():
        convert_md_to_pdf(md_file, pdf_file)
    print("All documentation converted to PDF successfully!")
