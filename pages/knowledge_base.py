"""
pages/knowledge_base.py
--------------------------
Knowledge Base page: lets the user view, add, and delete knowledge base
documents, and rebuild the vector database used for RAG retrieval.
"""

import os
import streamlit as st

from config.config import Config
from rag.document_loader import list_knowledge_base_files
from rag.retriever import rebuild_vector_database
from rag import vector_store

st.set_page_config(page_title="Knowledge Base", page_icon="📚", layout="wide")

st.title("📚 Knowledge Base")
st.caption("View, manage, and rebuild the RAG knowledge base used to answer IT support questions.")

st.divider()

# ---------------------------------------------------------------------------
# Vector database status + rebuild
# ---------------------------------------------------------------------------
st.markdown("### 🔄 Vector Database")

col1, col2 = st.columns([3, 1])
with col1:
    try:
        is_empty = vector_store.collection_is_empty()
        if is_empty:
            st.warning("The vector database is currently empty. Click 'Rebuild' to index the knowledge base.")
        else:
            st.success("The vector database is initialized and ready for retrieval.")
    except Exception as exc:
        st.error(f"Could not check vector database status: {exc}")

with col2:
    if st.button("🔄 Rebuild Vector Database", use_container_width=True):
        with st.spinner("Rebuilding vector database from knowledge base documents..."):
            result = rebuild_vector_database()
        if result.get("status") == "success":
            st.success(
                f"✅ Rebuilt successfully: {result['chunks_indexed']} chunks from "
                f"{result['documents_indexed']} documents."
            )
        else:
            st.error(f"❌ Rebuild failed: {result.get('message')}")

st.divider()

# ---------------------------------------------------------------------------
# Document listing / viewing / deleting
# ---------------------------------------------------------------------------
st.markdown("### 📄 Knowledge Base Documents")

files = list_knowledge_base_files()

if not files:
    st.info("No knowledge base documents found.")
else:
    for filename in files:
        with st.expander(f"📄 {filename}"):
            file_path = os.path.join(Config.KNOWLEDGE_BASE_DIR, filename)
            try:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                st.text_area("Content", value=content, height=250, key=f"view_{filename}", disabled=True)
            except Exception as exc:
                st.error(f"Could not read file: {exc}")

            delete_col, _ = st.columns([1, 4])
            with delete_col:
                confirm_key = f"confirm_delete_{filename}"
                if st.button(f"🗑️ Delete {filename}", key=f"delete_{filename}"):
                    st.session_state[confirm_key] = True

                if st.session_state.get(confirm_key):
                    st.warning(f"Are you sure you want to delete '{filename}'? This cannot be undone.")
                    yes_col, no_col = st.columns(2)
                    with yes_col:
                        if st.button("Yes, delete", key=f"yes_{filename}"):
                            try:
                                os.remove(file_path)
                                st.session_state[confirm_key] = False
                                st.success(f"Deleted {filename}. Remember to rebuild the vector database.")
                                st.rerun()
                            except Exception as exc:
                                st.error(f"Could not delete file: {exc}")
                    with no_col:
                        if st.button("Cancel", key=f"no_{filename}"):
                            st.session_state[confirm_key] = False
                            st.rerun()

st.divider()

# ---------------------------------------------------------------------------
# Add a new document
# ---------------------------------------------------------------------------
st.markdown("### ➕ Add a New Knowledge Base Document")

ALLOWED_EXTENSION = ".txt"
MAX_FILE_SIZE_BYTES = 2 * 1024 * 1024  # 2 MB safety limit

new_filename = st.text_input("Document filename (must end in .txt)", placeholder="example_topic.txt")
new_content = st.text_area("Document content", height=200, placeholder="Enter troubleshooting content here...")

if st.button("💾 Save Document"):
    if not new_filename.strip():
        st.error("Please provide a filename.")
    elif not new_filename.lower().endswith(ALLOWED_EXTENSION):
        st.error("Only .txt files are allowed for the knowledge base.")
    elif "/" in new_filename or "\\" in new_filename or ".." in new_filename:
        st.error("Invalid filename. Please use a simple filename without path characters.")
    elif not new_content.strip():
        st.error("Document content cannot be empty.")
    elif len(new_content.encode("utf-8")) > MAX_FILE_SIZE_BYTES:
        st.error("Document is too large (limit: 2 MB).")
    else:
        try:
            safe_path = os.path.join(Config.KNOWLEDGE_BASE_DIR, os.path.basename(new_filename))
            with open(safe_path, "w", encoding="utf-8") as f:
                f.write(new_content)
            st.success(f"Saved '{new_filename}'. Remember to rebuild the vector database to include it.")
            st.rerun()
        except Exception as exc:
            st.error(f"Could not save document: {exc}")
