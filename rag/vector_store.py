"""
rag/vector_store.py
---------------------
Persistent vector database wrapper built on ChromaDB.

ChromaDB was chosen over FAISS for this project because it:
- Installs cleanly on Windows with a simple `pip install chromadb`.
- Persists to disk automatically (no manual index save/load bookkeeping).
- Stores document text and metadata alongside vectors, simplifying retrieval.

Pipeline stage: Embedding Generation -> Vector Database -> Similarity Search
"""

import os
from typing import List, Dict

from config.config import Config
from rag.embeddings import embed_texts, embed_query
from rag.document_loader import load_and_chunk_documents

COLLECTION_NAME = "it_helpdesk_knowledge_base"

_client = None
_collection = None


def _get_client():
    """Create (once) and return a persistent ChromaDB client."""
    global _client
    if _client is None:
        import chromadb

        os.makedirs(Config.VECTOR_DB_DIR, exist_ok=True)
        _client = chromadb.PersistentClient(path=Config.VECTOR_DB_DIR)
    return _client


def _get_collection(reset: bool = False):
    """Return the Chroma collection, optionally deleting and recreating it."""
    global _collection
    client = _get_client()

    if reset:
        try:
            client.delete_collection(COLLECTION_NAME)
        except Exception:
            pass
        _collection = None

    if _collection is None:
        _collection = client.get_or_create_collection(name=COLLECTION_NAME)
    return _collection


def collection_is_empty() -> bool:
    """Return True if the vector database has no stored chunks yet."""
    try:
        collection = _get_collection()
        return collection.count() == 0
    except Exception:
        return True


def build_vector_database(kb_dir: str = None) -> Dict:
    """
    Rebuild the vector database from scratch using all documents currently
    present in the knowledge_base directory.

    Returns a status dictionary describing the outcome.
    """
    try:
        chunks = load_and_chunk_documents(kb_dir)
        if not chunks:
            return {"status": "error", "message": "No documents found in knowledge base."}

        collection = _get_collection(reset=True)

        texts = [c["text"] for c in chunks]
        ids = [f"{c['filename']}::{c['chunk_id']}" for c in chunks]
        metadatas = [{"filename": c["filename"], "chunk_id": c["chunk_id"]} for c in chunks]

        embeddings = embed_texts(texts)

        # Chroma requires plain python lists, not numpy arrays.
        collection.add(
            ids=ids,
            documents=texts,
            metadatas=metadatas,
            embeddings=embeddings.tolist(),
        )

        return {
            "status": "success",
            "chunks_indexed": len(chunks),
            "documents_indexed": len(set(c["filename"] for c in chunks)),
        }
    except Exception as exc:
        return {"status": "error", "message": str(exc)}


def similarity_search(query: str, top_k: int = None) -> List[Dict]:
    """
    Search the vector database for the chunks most similar to `query`.

    Returns a list of dicts: {"filename", "chunk_id", "text", "distance"}
    """
    top_k = top_k or Config.TOP_K_RESULTS
    try:
        if collection_is_empty():
            build_vector_database()

        collection = _get_collection()
        if collection.count() == 0:
            return []

        query_embedding = embed_query(query)
        results = collection.query(
            query_embeddings=[query_embedding.tolist()],
            n_results=min(top_k, collection.count()),
        )

        output = []
        documents = results.get("documents", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0]
        distances = results.get("distances", [[]])[0]

        for doc, meta, dist in zip(documents, metadatas, distances):
            output.append(
                {
                    "filename": meta.get("filename", "unknown"),
                    "chunk_id": meta.get("chunk_id", -1),
                    "text": doc,
                    "distance": dist,
                }
            )
        return output
    except Exception:
        return []
