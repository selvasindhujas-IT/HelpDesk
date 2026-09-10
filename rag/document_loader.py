"""
rag/document_loader.py
-----------------------
Loads text documents from the knowledge_base directory, cleans them, and
splits them into overlapping chunks suitable for embedding.

Pipeline stage: Documents -> Document Loader -> Text Cleaning -> Chunking
"""

import os
import re
from typing import List, Dict

from config.config import Config


def list_knowledge_base_files(kb_dir: str = None) -> List[str]:
    """Return a sorted list of .txt filenames available in the knowledge base."""
    kb_dir = kb_dir or Config.KNOWLEDGE_BASE_DIR
    if not os.path.isdir(kb_dir):
        return []
    files = [f for f in os.listdir(kb_dir) if f.lower().endswith(".txt")]
    return sorted(files)


def clean_text(text: str) -> str:
    """Normalize whitespace and strip control characters from raw text."""
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    # Collapse 3+ blank lines down to a double newline.
    text = re.sub(r"\n{3,}", "\n\n", text)
    # Strip trailing whitespace on each line.
    lines = [line.rstrip() for line in text.split("\n")]
    return "\n".join(lines).strip()


def load_documents(kb_dir: str = None) -> List[Dict]:
    """
    Load all knowledge base documents.

    Returns a list of dicts: {"filename": str, "content": str}
    """
    kb_dir = kb_dir or Config.KNOWLEDGE_BASE_DIR
    documents = []
    for filename in list_knowledge_base_files(kb_dir):
        file_path = os.path.join(kb_dir, filename)
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                raw = f.read()
            documents.append({"filename": filename, "content": clean_text(raw)})
        except (OSError, IOError):
            # Skip unreadable files but do not crash the pipeline.
            continue
    return documents


def chunk_text(text: str, chunk_size: int = None, overlap: int = None) -> List[str]:
    """
    Split text into overlapping chunks of roughly `chunk_size` characters.

    A word-boundary-aware sliding window is used so chunks do not cut words
    in half, and `overlap` characters are repeated between consecutive
    chunks to preserve context across chunk boundaries.
    """
    chunk_size = chunk_size or Config.CHUNK_SIZE
    overlap = overlap or Config.CHUNK_OVERLAP

    words = text.split()
    if not words:
        return []

    chunks = []
    current_words: List[str] = []
    current_len = 0

    for word in words:
        current_words.append(word)
        current_len += len(word) + 1
        if current_len >= chunk_size:
            chunks.append(" ".join(current_words))
            # Build the overlap for the next chunk from the tail of this one.
            overlap_words = []
            overlap_len = 0
            for w in reversed(current_words):
                overlap_len += len(w) + 1
                overlap_words.insert(0, w)
                if overlap_len >= overlap:
                    break
            current_words = overlap_words
            current_len = sum(len(w) + 1 for w in current_words)

    if current_words:
        chunks.append(" ".join(current_words))

    return chunks


def load_and_chunk_documents(kb_dir: str = None) -> List[Dict]:
    """
    Full loader pipeline: load every document and split it into chunks.

    Returns a list of dicts:
        {"filename": str, "chunk_id": int, "text": str}
    """
    documents = load_documents(kb_dir)
    all_chunks = []
    for doc in documents:
        chunks = chunk_text(doc["content"])
        for idx, chunk in enumerate(chunks):
            all_chunks.append(
                {
                    "filename": doc["filename"],
                    "chunk_id": idx,
                    "text": chunk,
                }
            )
    return all_chunks
