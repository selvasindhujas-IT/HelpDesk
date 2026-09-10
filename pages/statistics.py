"""
pages/statistics.py
----------------------
Statistics page: shows aggregate usage statistics computed from SQLite.
"""

import streamlit as st
import pandas as pd

from database import database

st.set_page_config(page_title="Statistics", page_icon="📊", layout="wide")

st.title("📊 Statistics")
st.caption("Project usage statistics: query volume, feedback, and problem category breakdown.")

st.divider()

try:
    database.init_database()
    stats = database.get_statistics()
except Exception as exc:
    st.error(f"Could not load statistics: {exc}")
    stats = None

if stats is None:
    st.stop()

if stats["total_queries"] == 0:
    st.info("No data yet. Ask a few questions on the AI Helpdesk page to generate statistics.")
else:
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Queries", stats["total_queries"])
    col2.metric("Helpful Responses", stats["helpful_responses"])
    col3.metric("Not Helpful", stats["not_helpful_responses"])
    col4.metric("Most Common Issue", stats["most_common_category"].title())

    st.divider()
    st.markdown("### Problem Category Breakdown")

    if stats["category_breakdown"]:
        df = pd.DataFrame(stats["category_breakdown"])
        df["category"] = df["category"].str.title()
        df = df.set_index("category")
        st.bar_chart(df["count"])
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No category data available yet.")

    st.divider()
    st.markdown("### Feedback Breakdown")
    feedback_df = pd.DataFrame(
        {
            "Feedback": ["Helpful", "Not Helpful", "No Feedback Yet"],
            "Count": [
                stats["helpful_responses"],
                stats["not_helpful_responses"],
                stats["no_feedback_yet"],
            ],
        }
    ).set_index("Feedback")
    st.bar_chart(feedback_df)
