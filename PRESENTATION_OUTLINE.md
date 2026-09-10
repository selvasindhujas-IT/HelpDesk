# Presentation Outline — 10 Slides

## Slide 1: Title
- **AI IT Helpdesk Agent**
- "An Intelligent AI-Powered IT Troubleshooting and Support System"
- Your name, college, department, guide name, date

## Slide 2: Introduction
- IT support problems are common but repetitive.
- Goal: build an AI agent that understands natural-language IT problems and
  provides accurate, step-by-step solutions.
- Combines AI Agent, RAG, and Tool Calling concepts.

## Slide 3: Problem Statement
- Users often can't self-diagnose IT issues.
- Human IT support isn't always available 24/7.
- Generic AI chatbots may hallucinate incorrect technical advice.
- Need: an always-available, knowledge-grounded, diagnostic-aware assistant.

## Slide 4: Existing System
- Static FAQ pages (manual searching required).
- Rigid rule-based chatbots (can't handle varied phrasing).
- Human helpdesk staff (doesn't scale, not always available).

## Slide 5: Proposed System
- AI Agent orchestrates: intent classification → RAG retrieval → tool
  calling → response generation.
- Grounded answers via a curated knowledge base.
- Live diagnostics specific to the user's machine.
- Works with or without an LLM API key (Demo Mode).

## Slide 6: Architecture
```
User → Streamlit UI → AI Agent → Intent Classification → RAG Retriever
→ Knowledge Base → Safe Diagnostic Tools → LLM / Demo Mode
→ Final Response → Memory → SQLite → Feedback
```

## Slide 7: Modules
- config, agent, rag, tools, memory, database, knowledge_base, pages
- Each module has a single clear responsibility (separation of concerns).

## Slide 8: Technologies
- Python 3.11+, Streamlit, Sentence Transformers, ChromaDB, SQLite,
  psutil, python-dotenv, Anthropic/OpenAI SDKs.

## Slide 9: Results
- Working chat interface with structured troubleshooting responses.
- RAG source attribution shown in the UI.
- Live system diagnostics dashboard.
- Chat history and statistics dashboards populated from real usage.
- Fully functional Demo Mode requiring zero external dependencies at runtime.

## Slide 10: Conclusion & Future Enhancements
- Successfully demonstrates AI Agent + RAG + Tool Calling in one project.
- Future: ML-based intent classification, voice input, multilingual support,
  real ticketing system integration, expanded diagnostic tools.
