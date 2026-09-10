"""
pages/history.py
-------------------
Chat History page: displays previously stored conversations from SQLite.
"""

import streamlit as st

from database import database

st.set_page_config(page_title="Chat History", page_icon="📜", layout="wide")

st.title("📜 Chat History")
st.caption("Browse previously asked questions, AI responses, categories, and feedback.")

st.divider()

try:
    database.init_database()
    records = database.get_all_chat_history(limit=300)
except Exception as exc:
    st.error(f"Could not load chat history: {exc}")
    records = []

if not records:
    st.info("No chat history yet. Ask a question on the AI Helpdesk page to get started.")
else:
    st.markdown(f"**Total conversations recorded:** {len(records)}")

    category_filter = st.selectbox(
        "Filter by category",
        options=["All"] + sorted(set(r["category"] for r in records if r["category"])),
    )

    feedback_icons = {"helpful": "👍 Helpful", "not_helpful": "👎 Not Helpful", "none": "— No feedback yet"}

    filtered = records if category_filter == "All" else [r for r in records if r["category"] == category_filter]

    for record in filtered:
        with st.expander(f"🗨️ {record['timestamp'][:19]} — {record['category'].title()} — {record['user_question'][:60]}"):
            st.markdown(f"**Date:** {record['timestamp']}")
            st.markdown(f"**Category:** {record['category']}")
            st.markdown("**User Question:**")
            st.write(record["user_question"])
            st.markdown("**AI Response:**")
            st.markdown(record["ai_response"])
            if record.get("sources"):
                st.markdown(f"**Knowledge Sources:** {record['sources']}")
            st.markdown(f"**Feedback:** {feedback_icons.get(record['feedback'], record['feedback'])}")
