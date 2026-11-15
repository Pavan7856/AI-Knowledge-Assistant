import os
from pathlib import Path
from typing import Dict, Any, List, Optional
import chromadb
from chromadb.utils import embedding_functions
from langchain_text_splitters import RecursiveCharacterTextSplitter
from google import genai

from backend.config import CHROMA_DIR

class RAGPipeline:
    """
    RAG Pipeline managing:
    1. Text Chunking (RecursiveCharacterTextSplitter)
    2. Embeddings & Vector Storage (ChromaDB)
    3. Similarity Search & Context Retrieval
    4. Contextual Q&A Generation with Google Gemini (Official google-genai SDK)
    """

    def __init__(self, collection_name: str = "enterprise_knowledge_base"):
        self.chroma_path = CHROMA_DIR
        self.collection_name = collection_name

        # Initialize Persistent ChromaDB Client
        self.chroma_client = chromadb.PersistentClient(path=str(self.chroma_path))

        # Default embedding function: all-MiniLM-L6-v2 ONNX local model
        self.embedding_fn = embedding_functions.DefaultEmbeddingFunction()

        # Get or create collection
        self.collection = self.chroma_client.get_or_create_collection(
            name=self.collection_name,
            embedding_function=self.embedding_fn,
            metadata={"description": "Enterprise AI Knowledge Base"}
        )

        # Text Splitter with chunk size and overlap
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=700,
            chunk_overlap=150,
            separators=["\n\n", "\n", ". ", " ", ""]
        )

        # Gemini API Setup
        self.api_key = os.getenv("GEMINI_API_KEY", "")
        self.client: Optional[genai.Client] = None
        self.llm_initialized = False
        self._init_gemini()

    def _init_gemini(self):
        """Initializes Google Gemini API client if valid key is present."""
        if self.api_key and self.api_key != "your_gemini_api_key_here":
            try:
                self.client = genai.Client(api_key=self.api_key)
                self.llm_initialized = True
            except Exception as e:
                print(f"[Warning] Failed to configure Gemini client: {e}")
                self.llm_initialized = False
        else:
            self.llm_initialized = False

    def set_api_key(self, api_key: str):
        """Allows setting or updating Gemini API key dynamically."""
        self.api_key = api_key.strip()
        self._init_gemini()

    def ingest_pdf_content(self, file_name: str, pages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Takes extracted pages, chunks text while tracking page numbers,
        generates embeddings, and stores them in ChromaDB.
        """
        all_chunks: List[str] = []
        all_metadatas: List[Dict[str, Any]] = []
        all_ids: List[str] = []

        chunk_counter = 0

        for page in pages:
            page_num = page["page_number"]
            page_text = page["text"].strip()
            if not page_text:
                continue

            page_chunks = self.text_splitter.split_text(page_text)
            for idx, chunk in enumerate(page_chunks):
                chunk_id = f"{file_name}_p{page_num}_c{idx}_{chunk_counter}"
                all_chunks.append(chunk)
                all_metadatas.append({
                    "source": file_name,
                    "page": page_num,
                    "chunk_index": idx
                })
                all_ids.append(chunk_id)
                chunk_counter += 1

        if all_chunks:
            # Batch upsert into ChromaDB
            self.collection.upsert(
                documents=all_chunks,
                metadatas=all_metadatas,
                ids=all_ids
            )

        return {
            "file_name": file_name,
            "total_chunks_created": chunk_counter,
            "total_docs_in_collection": self.collection.count()
        }

    def query(self, question: str, top_k: int = 3) -> Dict[str, Any]:
        """
        Retrieves relevant context from ChromaDB and generates answer via Gemini.
        """
        if self.collection.count() == 0:
            return {
                "answer": "No documents found in the Knowledge Base. Please upload and index a PDF document first.",
                "sources": [],
                "chunks_found": 0
            }

        # Query Vector Database
        results = self.collection.query(
            query_texts=[question],
            n_results=min(top_k, self.collection.count())
        )

        retrieved_docs = results.get("documents", [[]])[0]
        retrieved_metas = results.get("metadatas", [[]])[0]
        distances = results.get("distances", [[]])[0] if "distances" in results and results["distances"] else []

        sources = []
        context_parts = []

        for i, doc in enumerate(retrieved_docs):
            meta = retrieved_metas[i] if i < len(retrieved_metas) else {}
            dist = distances[i] if i < len(distances) else None
            page = meta.get("page", "Unknown")
            source_file = meta.get("source", "Unknown")

            sources.append({
                "source": source_file,
                "page": page,
                "snippet": doc[:250] + ("..." if len(doc) > 250 else ""),
                "distance": round(dist, 4) if dist is not None else None
            })
            context_parts.append(f"[Document: {source_file}, Page: {page}]\n{doc}")

        context_str = "\n\n---\n\n".join(context_parts)

        # Generate answer with LLM
        if self.llm_initialized and self.client:
            prompt = (
                "You are an Enterprise AI Knowledge Assistant.\n"
                "Answer the user's question accurately and concisely using ONLY the provided document context below.\n"
                "If the answer cannot be found in the context, clearly state: 'The requested information is not available in the provided document.'\n"
                "Always cite the relevant page number(s) where the answer was found.\n\n"
                f"Context:\n{context_str}\n\n"
                f"Question: {question}\n\n"
                "Answer:"
            )
            try:
                response = self.client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt
                )
                answer_text = response.text.strip() if response.text else "No answer generated."
            except Exception as e:
                answer_text = f"LLM Generation Error: {str(e)}\n\n(Context was successfully retrieved from ChromaDB. Please see retrieved references below)."
        else:
            top_snippet = sources[0]['snippet'] if sources else ''
            answer_text = (
                "⚠️ **Gemini API Key is not configured.**\n\n"
                "However, ChromaDB vector search successfully retrieved the most relevant context from your document. "
                "To enable full AI answer generation, please enter your Google Gemini API Key in the left sidebar.\n\n"
                f"**Top Retrieved Document Context:**\n\n> {top_snippet}"
            )

        return {
            "answer": answer_text,
            "sources": sources,
            "chunks_found": len(sources)
        }

    def reset_collection(self):
        """Clears all vectors in current collection."""
        self.chroma_client.delete_collection(self.collection_name)
        self.collection = self.chroma_client.get_or_create_collection(
            name=self.collection_name,
            embedding_function=self.embedding_fn
        )
        return {"status": "cleared", "total_docs": self.collection.count()}
