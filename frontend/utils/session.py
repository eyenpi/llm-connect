import streamlit as st


class SessionState:
    def __init__(self):
        self.token: str = ""
        self.conversations = []
        self.selected_conversation_id = None
        self.logged_in: bool = False

    @staticmethod
    def get() -> "SessionState":
        if not hasattr(st.session_state, "session"):
            st.session_state.session = SessionState()
        return st.session_state.session
