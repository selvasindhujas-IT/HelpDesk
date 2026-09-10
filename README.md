# AI IT Helpdesk Agent
### An Intelligent AI-Powered IT Troubleshooting and Support System

---

## 1. Project Title
**AI IT Helpdesk Agent** — An Intelligent AI-Powered IT Troubleshooting and Support System

## 2. Abstract
The AI IT Helpdesk Agent is a Python-based intelligent support system that helps
users diagnose and resolve common IT problems through natural-language
conversation. The system combines three core AI concepts — an **AI Agent**
that orchestrates the workflow, **Retrieval-Augmented Generation (RAG)** to
ground responses in a curated troubleshooting knowledge base, and **Tool
Calling** to run safe, predefined system diagnostics — to produce accurate,
step-by-step troubleshooting guidance. The system is built with Streamlit for
the user interface, Sentence Transformers and ChromaDB for the RAG pipeline,
and SQLite for persistent chat history and feedback storage. A fully
functional **Demo Mode** allows the entire system to be demonstrated without
any LLM API key.

## 3. Introduction
IT support is one of the most repetitive yet essential functions in any
organization or household. Many common problems (Wi-Fi issues, slow
computers, printer errors) follow well-known troubleshooting patterns that
can be automated. This project builds an AI agent that mimics a first-line
IT support technician: it listens to the user's problem in plain language,
retrieves the most relevant known solutions, checks the live system state
where useful, and presents a clear, structured diagnosis and solution.

## 4. Problem Statement
Users without technical expertise often struggle to describe, diagnose, and
resolve IT issues on their own, while human IT support may not always be
immediately available. There is a need for an accessible, always-available,
intelligent assistant that can interpret plain-language problem descriptions
and provide accurate, actionable troubleshooting steps grounded in real
technical documentation rather than generic or hallucinated advice.

## 5. Project Objectives
- Build a conversational AI agent for IT troubleshooting.
- Implement a RAG pipeline over a curated local knowledge base.
- Implement safe, predefined tool calling for live system diagnostics.
- Maintain conversation memory across a session.
- Persist chat history and collect user feedback.
- Provide a fully working Demo Mode requiring no external API access.
- Present a clean, professional, multi-page Streamlit interface.

## 6. Existing System
Traditional IT helpdesk systems rely on either (a) static FAQ pages that
require the user to search manually, (b) rule-based chatbots with rigid
decision trees that cannot handle varied phrasing, or (c) human support
staff, which does not scale and is not always available 24/7. None of these
combine live system diagnostics with grounded, retrieval-based knowledge in
a single conversational interface.

## 7. Proposed System
The proposed system introduces an AI Agent that intelligently orchestrates
intent classification, knowledge retrieval (RAG), and safe diagnostic tool
calls, then uses an LLM (or a rich Demo Mode fallback) to synthesize a clear,
structured response. This provides accuracy (grounded in a real knowledge
base), personalization (live diagnostics specific to the user's machine),
and availability (works without any external API when needed).

## 8. System Architecture
```
User
  ↓
Streamlit UI
  ↓
AI IT Helpdesk Agent
  ↓
Problem / Intent Classification
  ↓
RAG Retriever  →  Knowledge Base (10 topic documents)
  ↓
Safe Diagnostic Tools (psutil, socket, platform, restricted subprocess)
  ↓
LLM (Anthropic / OpenAI) or Demo Mode Templates
  ↓
Final Troubleshooting Response
  ↓
Conversation Memory (session-level)
  ↓
SQLite Database (chat_history table)
  ↓
Feedback (👍 / 👎)
```

## 9. Modules
| Module | Responsibility |
|---|---|
| `config/` | Centralized configuration, environment loading, Demo Mode detection |
| `agent/` | Intent classification, tool-call decisions, LLM/Demo response generation |
| `rag/` | Document loading, chunking, embeddings, vector store, retrieval |
| `tools/` | Safe, predefined system diagnostic functions |
| `memory/` | In-session conversation memory |
| `database/` | SQLite persistence for chat history and feedback |
| `knowledge_base/` | 10 plain-text troubleshooting documents |
| `pages/` | Streamlit multipage UI: Diagnostics, Knowledge Base, History, Statistics, About |

## 10. Technologies Used
- **Language:** Python 3.11+
- **Frontend:** Streamlit
- **Embeddings:** Sentence Transformers (`all-MiniLM-L6-v2`)
- **Vector Database:** ChromaDB (persistent, local)
- **LLM SDKs:** `anthropic`, `openai` (configurable via `.env`)
- **Database:** SQLite (standard library `sqlite3`)
- **Diagnostics:** `psutil`, `socket`, `platform`, `subprocess` (ping only)
- **Configuration:** `python-dotenv`

## 11. Hardware Requirements
- A laptop or desktop with at least 4 GB RAM (8 GB recommended)
- At least 2 GB free disk space (for Python packages and the embedding model)
- Internet connection (for installing dependencies and, optionally, live LLM calls)

## 12. Software Requirements
- Windows 10/11 (also runs on macOS/Linux)
- Python 3.11 or later
- pip (Python package manager)

## 13. Installation

```bash
# 1. Extract the project
cd AI_IT_Helpdesk_Agent

# 2. Create a virtual environment
python -m venv venv
```

## 14. Virtual Environment Setup

**Windows:**
```bash
venv\Scripts\activate
```

**macOS/Linux:**
```bash
source venv/bin/activate
```

## 15. Dependency Installation

```bash
pip install -r requirements.txt
```

> The first run will also download the `all-MiniLM-L6-v2` Sentence Transformer
> model (a few hundred MB) — this requires an internet connection once.

## 16. API Key Configuration

1. Copy `.env.example` to `.env`
2. Open `.env` and set:
   ```
   LLM_PROVIDER=anthropic
   LLM_API_KEY=your_real_api_key_here
   LLM_MODEL=claude-3-5-sonnet-20241022
   ```
3. Save the file. Never commit `.env` to version control (it is already
   listed in `.gitignore`).

## 17. Demo Mode
If `LLM_API_KEY` is left blank in `.env` (or `.env` does not exist), the
application automatically detects this and runs in **🟡 Demo Mode**:
- A yellow banner is displayed in the UI.
- All chat responses use rich, pre-written templates per problem category.
- RAG retrieval, tool calling, memory, history, and feedback all continue to
  work exactly as in Live Mode — only the final response generation differs.

## 18. How to Run

```bash
streamlit run app.py
```

Streamlit will open the application automatically in your default web
browser (typically at `http://localhost:8501`).

## 19. How RAG Works
1. All `.txt` files in `knowledge_base/` are loaded and cleaned.
2. Each document is split into overlapping ~400-character chunks.
3. Each chunk is embedded into a vector using Sentence Transformers.
4. Vectors are stored in a persistent ChromaDB collection.
5. When a user asks a question, the question is embedded the same way and
   compared against all stored chunk vectors using similarity search.
6. The top-k most similar chunks are returned and used as grounding context
   for the LLM (or to select the correct Demo Mode template).
7. The originating filenames are displayed in the UI as "Knowledge Sources
   Used".

## 20. How Agent Works
The `HelpdeskAgent` pipeline (in `agent/helpdesk_agent.py`) performs, for
every user query:
1. Keyword-based intent/category classification (10 categories + general).
2. RAG retrieval of relevant knowledge base chunks.
3. Decision logic to determine which (if any) diagnostic tools are relevant
   to the detected category.
4. Execution of those tools.
5. Combination of retrieved knowledge + diagnostic results into a single
   context, passed to the LLM (or Demo Mode templates) to produce the final,
   structured response.

## 21. How Tool Calling Works
`tools/system_tools.py` exposes a fixed set of safe, read-only diagnostic
functions (system info, hostname, local IP, internet check, DNS check, ping,
CPU/memory/disk usage). The agent decides which functions to call based on
the detected problem category — **no user input is ever passed into a shell
command**, and no destructive or credential-related operation is possible.

## 22. Database
SQLite database file: `data/helpdesk.db`, table `chat_history`:

| Column | Description |
|---|---|
| id | Auto-incrementing primary key |
| session_id | Identifier for the browser session |
| user_question | The question the user typed |
| ai_response | The full structured AI response |
| category | Detected problem category |
| sources | Comma-separated knowledge base filenames used |
| feedback | `none` / `helpful` / `not_helpful` |
| timestamp | ISO-formatted timestamp |

## 23. Testing
See `TEST_CASES.md` for the full set of 15 documented test cases covering
Wi-Fi, internet, DNS, performance, printer, Bluetooth, software, Windows, IP
lookup, network, login, empty input, missing API key, and tool failure
scenarios.

## 24. Advantages
- Fully functional without any external API (Demo Mode).
- Modular and easy to extend with new categories or tools.
- Grounded answers via RAG reduce the risk of incorrect/generic advice.
- Strong, explicit security boundaries around tool execution.

## 25. Limitations
- Keyword-based intent classification is simpler than a trained ML model.
- Demo Mode responses are template-based, not dynamically generated.
- Diagnostic tools cover common checks only, not deep hardware diagnostics.

## 26. Future Enhancements
- Replace keyword classification with a trained/fine-tuned classifier.
- Add voice input and multilingual support.
- Integrate with real ticketing systems.
- Expand the diagnostic tool set (Wi-Fi signal strength, driver versions).
- Add authentication and multi-user support for enterprise deployment.

## 27. Conclusion
The AI IT Helpdesk Agent demonstrates a practical, end-to-end integration of
AI agent design, Retrieval-Augmented Generation, and safe tool calling to
solve a real-world support problem. Its modular architecture, working Demo
Mode, and comprehensive feature set make it well-suited as a college
final-year project deliverable, viva demonstration, and foundation for
further development.

---

## Project Folder Structure
```
AI_IT_Helpdesk_Agent/
│
├── app.py
├── requirements.txt
├── README.md
├── TEST_CASES.md
├── VIVA_QUESTIONS.md
├── PRESENTATION_OUTLINE.md
├── DEMO_INSTRUCTIONS.md
├── .env.example
├── .gitignore
│
├── config/
│   ├── __init__.py
│   └── config.py
│
├── agent/
│   ├── __init__.py
│   └── helpdesk_agent.py
│
├── rag/
│   ├── __init__.py
│   ├── document_loader.py
│   ├── embeddings.py
│   ├── vector_store.py
│   └── retriever.py
│
├── tools/
│   ├── __init__.py
│   └── system_tools.py
│
├── memory/
│   ├── __init__.py
│   └── conversation_memory.py
│
├── database/
│   ├── __init__.py
│   └── database.py
│
├── knowledge_base/
│   ├── wifi.txt
│   ├── internet.txt
│   ├── windows.txt
│   ├── printer.txt
│   ├── bluetooth.txt
│   ├── software.txt
│   ├── network.txt
│   ├── performance.txt
│   ├── login.txt
│   └── dns.txt
│
├── data/
│   └── .gitkeep
│
└── pages/
    ├── diagnostics.py
    ├── knowledge_base.py
    ├── history.py
    ├── statistics.py
    └── about.py
```
