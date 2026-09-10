"""
pages/about.py
-----------------
About page: project overview for demonstration and viva purposes.
"""

import streamlit as st
from config.config import Config

st.set_page_config(page_title="About", page_icon="ℹ️", layout="wide")

st.title("ℹ️ About This Project")

st.markdown(f"## {Config.APP_TITLE}")
st.caption(Config.APP_SUBTITLE)

st.divider()

st.markdown("""
### Project Objective
To design and implement an AI-powered IT Helpdesk Agent capable of understanding
natural-language descriptions of common computer problems, retrieving relevant
troubleshooting knowledge using Retrieval-Augmented Generation (RAG), running
safe diagnostic tools, and generating clear, step-by-step solutions — while
remembering conversation context and logging feedback for continuous
improvement.

### Technologies Used
- **Language:** Python 3.11+
- **Frontend:** Streamlit
- **AI / LLM:** Configurable LLM provider (Anthropic Claude or OpenAI), with a
  fully functional local Demo Mode when no API key is present
- **RAG:** Sentence Transformers for embeddings, ChromaDB for vector storage
  and similarity search
- **Database:** SQLite for chat history and feedback
- **Diagnostics:** `psutil`, `socket`, `platform`, and a restricted `subprocess`
  call (ping only, hardcoded arguments)
- **Configuration:** `python-dotenv`

### Main Features
1. AI Helpdesk Chat with structured, step-by-step responses
2. RAG-based knowledge base search across 10 IT topics
3. AI Agent layer for intent classification and orchestration
4. Safe, predefined diagnostic tool calling
5. Conversation memory for context-aware follow-ups
6. SQLite-backed chat history
7. User feedback capture (👍 / 👎)
8. System Diagnostics dashboard
9. Knowledge Base management (view / add / delete / rebuild index)
10. Statistics dashboard with category and feedback breakdowns

### System Architecture
```
User → Streamlit UI → AI Agent → Intent Classification → RAG Retriever
     → Knowledge Base → Safe Diagnostic Tools → LLM (or Demo Mode)
     → Final Response → Conversation Memory → SQLite Database → Feedback
```

### Advantages
- Works fully offline in Demo Mode — no API key required for demonstration.
- Modular, well-separated codebase (agent / rag / tools / memory / database).
- Extensible knowledge base — new topics can be added without code changes.
- Strong safety boundaries: no arbitrary command execution, no credential
  access, no destructive system operations.

### Limitations
- The rule-based intent classifier uses keyword matching rather than a
  trained ML classifier, so ambiguous queries may be miscategorized.
- Demo Mode responses are template-based rather than dynamically generated.
- The knowledge base currently covers 10 common categories; highly specific
  or hardware-level issues may fall back to general guidance.

### Future Enhancements
- Add a fine-tuned intent classification model.
- Support voice input and multi-language responses.
- Integrate with real ticketing systems (e.g., Jira Service Desk).
- Add role-based access control for enterprise deployment.
- Expand the diagnostic tool set (e.g., Wi-Fi signal strength, driver version
  checks).
""")
