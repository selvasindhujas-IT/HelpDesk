"""
config/config.py
-----------------
Central configuration for the AI IT Helpdesk Agent.

Loads settings from environment variables (via a .env file) and exposes
them as simple constants / a Config class for the rest of the application.

No API key is ever hardcoded here. If LLM_API_KEY is missing or empty,
the application automatically falls back to DEMO MODE.
"""

import os
from dotenv import load_dotenv

# Load variables from a .env file in the project root (if present).
load_dotenv()

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KNOWLEDGE_BASE_DIR = os.path.join(BASE_DIR, "knowledge_base")
DATA_DIR = os.path.join(BASE_DIR, "data")
VECTOR_DB_DIR = os.path.join(DATA_DIR, "vector_store")
SQLITE_DB_PATH = os.path.join(DATA_DIR, "helpdesk.db")

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(VECTOR_DB_DIR, exist_ok=True)
os.makedirs(KNOWLEDGE_BASE_DIR, exist_ok=True)

# ---------------------------------------------------------------------------
# LLM configuration
# ---------------------------------------------------------------------------
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "anthropic").strip().lower()
LLM_API_KEY = os.getenv("LLM_API_KEY", "").strip()
LLM_MODEL = os.getenv("LLM_MODEL", "claude-3-5-sonnet-20241022").strip()

# The app runs in DEMO MODE whenever no API key has been configured.
DEMO_MODE = len(LLM_API_KEY) == 0

# ---------------------------------------------------------------------------
# RAG configuration
# ---------------------------------------------------------------------------
EMBEDDING_MODEL_NAME = os.getenv("EMBEDDING_MODEL_NAME", "all-MiniLM-L6-v2")
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "400"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "60"))
TOP_K_RESULTS = int(os.getenv("TOP_K_RESULTS", "3"))

# ---------------------------------------------------------------------------
# Diagnostics configuration
# ---------------------------------------------------------------------------
PING_TARGET_HOST = os.getenv("PING_TARGET_HOST", "8.8.8.8")
DNS_TEST_HOST = os.getenv("DNS_TEST_HOST", "www.google.com")

# ---------------------------------------------------------------------------
# Application metadata
# ---------------------------------------------------------------------------
APP_TITLE = "AI IT Helpdesk Agent"
APP_SUBTITLE = "Intelligent IT Troubleshooting Assistant"

PROBLEM_CATEGORIES = [
    "wifi",
    "internet",
    "windows",
    "printer",
    "bluetooth",
    "software",
    "network",
    "performance",
    "login",
    "dns",
    "general",
]


class Config:
    """Convenience wrapper so other modules can do `from config.config import Config`."""

    BASE_DIR = BASE_DIR
    KNOWLEDGE_BASE_DIR = KNOWLEDGE_BASE_DIR
    DATA_DIR = DATA_DIR
    VECTOR_DB_DIR = VECTOR_DB_DIR
    SQLITE_DB_PATH = SQLITE_DB_PATH

    LLM_PROVIDER = LLM_PROVIDER
    LLM_API_KEY = LLM_API_KEY
    LLM_MODEL = LLM_MODEL
    DEMO_MODE = DEMO_MODE

    EMBEDDING_MODEL_NAME = EMBEDDING_MODEL_NAME
    CHUNK_SIZE = CHUNK_SIZE
    CHUNK_OVERLAP = CHUNK_OVERLAP
    TOP_K_RESULTS = TOP_K_RESULTS

    PING_TARGET_HOST = PING_TARGET_HOST
    DNS_TEST_HOST = DNS_TEST_HOST

    APP_TITLE = APP_TITLE
    APP_SUBTITLE = APP_SUBTITLE
    PROBLEM_CATEGORIES = PROBLEM_CATEGORIES
