import streamlit as st
import requests
import os

# Backend API Configuration
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

# Page Configuration
st.set_page_config(
    page_title="Enterprise AI Knowledge Assistant",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Enterprise CSS Styling
st.markdown("""
<style>
    .main-title {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1565C0;
        margin-bottom: 0.1rem;
    }
    .phase-badge {
        background-color: #E3F2FD;
        color: #0D47A1;
        padding: 4px 12px;
        border-radius: 12px;
        font-weight: 600;
        font-size: 0.85rem;
        display: inline-block;
        margin-bottom: 1.2rem;
    }
    .answer-card {
        background-color: #F8FBF8;
        border-left: 5px solid #2E7D32;
        border-top: 1px solid #E0E0E0;
        border-right: 1px solid #E0E0E0;
        border-bottom: 1px solid #E0E0E0;
        padding: 20px;
        border-radius: 6px;
        margin-top: 15px;
        font-size: 1.05rem;
        line-height: 1.6;
        color: #1A1A1A;
    }
    .metric-container {
        background: #FAFAFA;
        border: 1px solid #EEEEEE;
        border-radius: 8px;
        padding: 12px;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# App Header
st.markdown('<div class="main-title">🧠 Mini Enterprise AI Knowledge Assistant</div>', unsafe_allow_html=True)
st.markdown('<span class="phase-badge">Phase 2: RAG Pipeline • ChromaDB Vector DB • Google Gemini LLM</span>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.header("⚙️ System Status")

    backend_online = False
    total_vectors = 0
    llm_connected = False

    try:
        health_resp = requests.get(f"{BACKEND_URL}/health", timeout=3)
        if health_resp.status_code == 200:
            health_data = health_resp.json()
            backend_online = True
            total_vectors = health_data.get("total_vectors", 0)
            llm_connected = health_data.get("llm_connected", False)

            st.success("🟢 Backend API: Online (Port 8000)")
            st.info(f"📊 Indexed Vectors in ChromaDB: **{total_vectors}**")
            if llm_connected:
                st.success("🤖 Gemini LLM: Connected")
            else:
                st.warning("⚠️ Gemini LLM: API Key Not Set")
        else:
            st.warning("🟡 Backend Status: Unknown")
    except Exception:
        st.error("🔴 Backend API: Offline")
        st.caption("Start backend in terminal:\n`uvicorn backend.main:app --reload --port 8000`")

    st.markdown("---")
    st.header("🔑 Google Gemini API Key")
    api_key_input = st.text_input(
        "API Key (Free Tier)",
        type="password",
        help="Obtain free API key from Google AI Studio (aistudio.google.com)"
    )
    if st.button("Save API Key", use_container_width=True):
        if api_key_input.strip():
            try:
                res = requests.post(f"{BACKEND_URL}/api/set-gemini-key", json={"api_key": api_key_input.strip()})
                if res.status_code == 200 and res.json().get("llm_connected"):
                    st.success("Gemini API Key connected successfully!")
                    st.rerun()
                else:
                    st.error("Failed to validate key.")
            except Exception as e:
                st.error(f"Error: {e}")

    st.markdown("---")
    st.header("📁 Document Ingestion")
    uploaded_file = st.file_uploader(
        "Upload PDF Document",
        type=["pdf"],
        help="PDF files will be extracted, chunked, and embedded into ChromaDB"
    )

    upload_btn = st.button("🚀 Upload & Index Document", type="primary", use_container_width=True, disabled=not backend_online)

    if total_vectors > 0:
        st.markdown("---")
        if st.button("🗑️ Clear Vector Database", use_container_width=True):
            try:
                requests.post(f"{BACKEND_URL}/api/reset-database")
                st.success("Knowledge base cleared successfully!")
                st.rerun()
            except Exception as e:
                st.error(f"Error clearing database: {e}")

# Handle Document Upload & Ingestion
if upload_btn and uploaded_file is not None:
    with st.spinner("Extracting text, chunking, and indexing embeddings into ChromaDB..."):
        try:
            files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")}
            response = requests.post(f"{BACKEND_URL}/api/upload-pdf", files=files, timeout=90)

            if response.status_code == 200:
                data = response.json()
                st.success(f"✅ Document '{data['file_name']}' successfully indexed into RAG Knowledge Base!")

                # Ingestion Metrics
                c1, c2, c3, c4 = st.columns(4)
                with c1:
                    st.metric("Total Pages", data["total_pages"])
                with c2:
                    st.metric("Characters", f"{data['total_chars']:,}")
                with c3:
                    st.metric("Chunks Generated", data["chunks_indexed"])
                with c4:
                    st.metric("Total Chunks in DB", data["total_knowledge_base_chunks"])

                with st.expander("📖 Extracted Text Preview (First 1,000 Characters)"):
                    st.text(data["preview"])
            else:
                st.error(f"Upload failed: {response.text}")
        except Exception as e:
            st.error(f"Could not connect to backend server: {e}")

# Main Content Area: RAG Question Answering
st.markdown("### 💬 Ask Questions From Your Documents (RAG Search)")

if total_vectors == 0:
    st.info("👈 Upload and index a PDF document using the left sidebar to start asking questions.")
else:
    col_q, col_k = st.columns([4, 1])
    with col_q:
        user_question = st.text_input(
            "Enter your question:",
            placeholder="e.g., What is the difference between list and tuple? or Summarize the main architecture components.",
            key="user_q"
        )
    with col_k:
        top_k = st.slider("Context Depth (Top Chunks)", min_value=1, max_value=5, value=3)

    ask_button = st.button("🔍 Ask AI Assistant", type="primary")

    if ask_button and user_question.strip():
        with st.spinner("Retrieving relevant context from ChromaDB and generating answer..."):
            try:
                res = requests.post(
                    f"{BACKEND_URL}/api/query",
                    json={"question": user_question.strip(), "top_k": top_k},
                    timeout=60
                )
                if res.status_code == 200:
                    ans_data = res.json()

                    # Answer Display
                    st.markdown("#### 💡 AI Generated Answer:")
                    st.markdown(f'<div class="answer-card">{ans_data["answer"]}</div>', unsafe_allow_html=True)

                    # Source Citations
                    sources = ans_data.get("sources", [])
                    if sources:
                        st.markdown("---")
                        st.markdown("#### 📑 Retrieved Sources & Page Citations:")
                        for idx, src in enumerate(sources):
                            with st.expander(f"📌 Reference {idx + 1}: {src['source']} (Page {src['page']})"):
                                st.write(f"**Context Snippet:** {src['snippet']}")
                                if src.get("distance") is not None:
                                    st.caption(f"Vector Similarity Distance: {src['distance']}")
                else:
                    st.error(f"Query Error: {res.text}")
            except Exception as e:
                st.error(f"Server communication failed: {e}")

# Footer
st.markdown("---")
st.caption("Enterprise AI Knowledge Assistant • Powered by FastAPI, LangChain, ChromaDB & Google Gemini")
