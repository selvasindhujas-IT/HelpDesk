"""
app.py
-------
Main entry point for the AI IT Helpdesk Agent Streamlit application.

This file sets up the page configuration, sidebar navigation, and renders
the Home dashboard and the main AI Helpdesk chat interface. Other pages
(System Diagnostics, Knowledge Base, Chat History, Statistics, About) live
in the `pages/` directory and are automatically picked up by Streamlit's
multipage app feature.
"""

import streamlit as st

from config.config import Config
from database import database
from memory.conversation_memory import ConversationMemory
from agent.helpdesk_agent import process_user_query
from rag.retriever import ensure_vector_database_ready

# ---------------------------------------------------------------------------
# Page configuration (must be the first Streamlit command)
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title=Config.APP_TITLE,
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# One-time initialization
# ---------------------------------------------------------------------------
database.init_database()

if "memory" not in st.session_state:
    st.session_state.memory = ConversationMemory()

if "chat_display" not in st.session_state:
    st.session_state.chat_display = []  # list of dicts for rendering

if "vector_db_ready" not in st.session_state:
    try:
        ensure_vector_database_ready()
        st.session_state.vector_db_ready = True
    except Exception as exc:
        st.session_state.vector_db_ready = False
        st.session_state.vector_db_error = str(exc)

if "example_query" not in st.session_state:
    st.session_state.example_query = ""

EXAMPLE_QUESTIONS = [
    "Wi-Fi connected but no internet",
    "My laptop is very slow",
    "Printer is not printing",
    "Bluetooth is not connecting",
    "Application is not opening",
    "How can I check my IP address?",
]


def render_mode_banner():
    if Config.DEMO_MODE:
        st.warning(
            "🟡 **DEMO MODE** — No LLM API key configured. Using local knowledge base "
            "and predefined responses. All RAG, tool calling, and memory features are "
            "still fully functional. Add a key to `.env` to enable live LLM responses.",
            icon="🟡",
        )
    else:
        st.success(f"🟢 **LIVE MODE** — Connected to LLM provider: `{Config.LLM_PROVIDER}` ({Config.LLM_MODEL})", icon="🟢")


def render_sidebar():
    with st.sidebar:
        st.markdown(f"## {Config.APP_TITLE}")
        st.caption(Config.APP_SUBTITLE)
        st.divider()
        st.markdown("### Navigation")
        st.page_link("app.py", label="🏠 Home")
        st.page_link("pages/diagnostics.py", label="🛠️ System Diagnostics")
        st.page_link("pages/knowledge_base.py", label="📚 Knowledge Base")
        st.page_link("pages/history.py", label="📜 Chat History")
        st.page_link("pages/statistics.py", label="📊 Statistics")
        st.page_link("pages/about.py", label="ℹ️ About")
        st.divider()
        if Config.DEMO_MODE:
            st.caption("🟡 Running in Demo Mode")
        else:
            st.caption(f"🟢 Live LLM: {Config.LLM_PROVIDER}")


def render_home_dashboard():
    st.title("🤖 AI IT Helpdesk Agent")
    st.caption(Config.APP_SUBTITLE)
    render_mode_banner()

    st.markdown(
        "An intelligent AI-powered IT support system that understands your problem, "
        "searches a local troubleshooting knowledge base using **RAG**, runs safe "
        "**diagnostic tools**, and generates a clear, step-by-step solution."
    )

    st.markdown("### Key Capabilities")
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        st.info("🤖 **AI Agent**\n\nClassifies your problem and orchestrates the full pipeline.")
    with c2:
        st.info("📚 **RAG**\n\nRetrieves relevant troubleshooting knowledge automatically.")
    with c3:
        st.info("🛠️ **Tools**\n\nRuns safe, predefined system diagnostics.")
    with c4:
        st.info("🧠 **Memory**\n\nRemembers the current conversation for follow-ups.")
    with c5:
        st.info("📊 **Analytics**\n\nTracks history, feedback, and usage statistics.")

    st.markdown("### How It Works")
    st.markdown(
        "`User Problem` → `AI Agent` → `RAG` → `Tools` → `Diagnosis` → `Solution`"
    )
    st.divider()


def render_example_buttons():
    st.markdown("**Try an example problem:**")
    cols = st.columns(3)
    for idx, question in enumerate(EXAMPLE_QUESTIONS):
        col = cols[idx % 3]
        if col.button(question, key=f"example_{idx}", use_container_width=True):
            st.session_state.example_query = question
            st.rerun()


def handle_feedback(record_id: int, feedback_value: str, chat_idx: int):
    if database.update_feedback(record_id, feedback_value):
        st.session_state.chat_display[chat_idx]["feedback"] = feedback_value
        st.toast("Thank you for your feedback!", icon="✅")
    else:
        st.toast("Could not save feedback (database error).", icon="⚠️")


def render_chat_interface():
    st.markdown("## 💬 AI Helpdesk Chat")

    if not st.session_state.vector_db_ready:
        st.error(
            "⚠️ The knowledge base vector database could not be initialized: "
            f"{st.session_state.get('vector_db_error', 'unknown error')}. "
            "You can still chat, but retrieval quality may be limited. "
            "Try rebuilding it from the Knowledge Base page."
        )

    render_example_buttons()
    st.divider()

    # Render prior turns.
    for idx, turn in enumerate(st.session_state.chat_display):
        with st.chat_message("user"):
            st.write(turn["question"])
        with st.chat_message("assistant"):
            st.markdown(turn["response"])
            if turn.get("sources"):
                with st.expander("📚 Knowledge Sources Used"):
                    for s in turn["sources"]:
                        st.write(f"- {s}")
            fb_col1, fb_col2, fb_spacer = st.columns([1, 1, 6])
            current_feedback = turn.get("feedback", "none")
            with fb_col1:
                if st.button(
                    "👍 Helpful",
                    key=f"helpful_{idx}",
                    type="primary" if current_feedback == "helpful" else "secondary",
                ):
                    handle_feedback(turn["record_id"], "helpful", idx)
                    st.rerun()
            with fb_col2:
                if st.button(
                    "👎 Not Helpful",
                    key=f"not_helpful_{idx}",
                    type="primary" if current_feedback == "not_helpful" else "secondary",
                ):
                    handle_feedback(turn["record_id"], "not_helpful", idx)
                    st.rerun()

    # Chat input.
    default_text = st.session_state.example_query
    user_input = st.chat_input("Describe your IT problem (e.g. 'My Wi-Fi is connected but internet is not working.')")

    if not user_input and default_text:
        user_input = default_text
        st.session_state.example_query = ""

    if user_input:
        st.session_state.memory.add_user_message(user_input)

        with st.spinner("Analyzing your problem..."):
            try:
                history_text = st.session_state.memory.get_recent_history_text()
                result = process_user_query(user_input, history_text=history_text)
            except Exception as exc:
                result = {
                    "category": "general",
                    "response_text": (
                        "⚠️ Something went wrong while processing your request. "
                        f"Technical details: {exc}\n\nPlease try rephrasing your problem, "
                        "or check the System Diagnostics page."
                    ),
                    "sources": [],
                    "used_llm": False,
                    "diagnostics": {},
                }

        st.session_state.memory.add_assistant_message(result["response_text"], category=result["category"])

        try:
            record_id = database.insert_chat_record(
                session_id=st.session_state.memory.session_id,
                user_question=user_input,
                ai_response=result["response_text"],
                category=result["category"],
                sources=", ".join(result["sources"]),
            )
        except Exception:
            record_id = -1

        st.session_state.chat_display.append(
            {
                "question": user_input,
                "response": result["response_text"],
                "sources": result["sources"],
                "record_id": record_id,
                "feedback": "none",
            }
        )
        st.rerun()


def main():
    render_sidebar()
    render_home_dashboard()
    render_chat_interface()


main()
