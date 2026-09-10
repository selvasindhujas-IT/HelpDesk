"""
rag/retriever.py
------------------
High-level retrieval interface used by the AI Agent.

Pipeline stage: Top-K Relevant Chunks -> LLM Context
"""

from typing import List, Dict

from config.config import Config
from rag import vector_store


def retrieve_context(query: str, top_k: int = None) -> Dict:
    """
    Retrieve the top-k most relevant knowledge base chunks for a query.

    Returns:
        {
            "chunks": [ {filename, chunk_id, text, distance}, ... ],
            "sources": ["wifi.txt", "internet.txt", ...],   # unique, ordered
            "context_text": "combined text used as LLM context"
        }
    """
    top_k = top_k or Config.TOP_K_RESULTS
    chunks = vector_store.similarity_search(query, top_k=top_k)

    sources = []
    for c in chunks:
        if c["filename"] not in sources:
            sources.append(c["filename"])

    context_text = "\n\n---\n\n".join(
        f"[Source: {c['filename']}]\n{c['text']}" for c in chunks
    )

    return {
        "chunks": chunks,
        "sources": sources,
        "context_text": context_text,
    }


def ensure_vector_database_ready() -> None:
    """Build the vector database if it does not already contain data."""
    if vector_store.collection_is_empty():
        vector_store.build_vector_database()


def rebuild_vector_database() -> Dict:
    """Force a full rebuild of the vector database. Used by the UI button."""
    return vector_store.build_vector_database()
