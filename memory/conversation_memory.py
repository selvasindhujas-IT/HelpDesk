"""
memory/conversation_memory.py
-------------------------------
Simple in-session conversation memory for the AI IT Helpdesk Agent.

This keeps track of the current conversation turns (user + assistant
messages) and the most recently discussed problem category, so the agent
can understand follow-up messages like "yes" or "it's still not working"
in the context of the earlier question.

The memory lives for the duration of a Streamlit session (stored in
st.session_state by the caller) - this class itself is a plain Python
object with no external dependencies, which also makes it easy to unit test.
"""

from typing import List, Dict, Optional
from datetime import datetime

MAX_TURNS_REMEMBERED = 12


class ConversationMemory:
    """Holds the rolling history of a single chat session."""

    def __init__(self):
        self.turns: List[Dict] = []
        self.last_category: Optional[str] = None
        self.session_id: str = datetime.now().strftime("%Y%m%d%H%M%S%f")

    def add_user_message(self, message: str) -> None:
        self.turns.append(
            {"role": "user", "content": message, "timestamp": datetime.now().isoformat()}
        )
        self._trim()

    def add_assistant_message(self, message: str, category: Optional[str] = None) -> None:
        self.turns.append(
            {"role": "assistant", "content": message, "timestamp": datetime.now().isoformat()}
        )
        if category:
            self.last_category = category
        self._trim()

    def _trim(self) -> None:
        """Keep only the most recent turns to avoid unbounded growth."""
        if len(self.turns) > MAX_TURNS_REMEMBERED:
            self.turns = self.turns[-MAX_TURNS_REMEMBERED:]

    def get_recent_history_text(self, max_turns: int = 6) -> str:
        """Return the last few turns formatted as plain text, for LLM context."""
        recent = self.turns[-max_turns:]
        lines = []
        for turn in recent:
            speaker = "User" if turn["role"] == "user" else "Assistant"
            lines.append(f"{speaker}: {turn['content']}")
        return "\n".join(lines)

    def get_last_category(self) -> Optional[str]:
        return self.last_category

    def clear(self) -> None:
        self.turns = []
        self.last_category = None
