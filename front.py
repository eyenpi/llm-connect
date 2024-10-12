import streamlit as st
from frontend.services.auth import AuthService
from frontend.services.conversation import ConversationService
from frontend.utils.logger import setup_logger

logger = setup_logger(__name__)


class ChatApp:
    def __init__(self):
        # Initialize session state if it is not yet initialized
        if "logged_in" not in st.session_state:
            st.session_state.logged_in = False
        if "token" not in st.session_state:
            st.session_state.token = None

    def run(self) -> None:
        if not st.session_state.logged_in:
            self.show_auth_page()
        else:
            self.show_conversation_page()

    def show_auth_page(self) -> None:
        st.title("Login/Register")
        choice = st.radio("Choose Action", ("Login", "Register"))
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        if st.button(f"{choice}"):
            if choice == "Login":
                self.login(email, password)
            else:
                self.register(email, password)

    def login(self, email: str, password: str) -> None:
        token = AuthService.login(email, password)
        if token:
            st.session_state.token = token
            st.session_state.logged_in = True  # Mark user as logged in
            st.success("Login successful!")
            st.rerun()
        else:
            st.error("Login failed!")

    def register(self, email: str, password: str) -> None:
        response = AuthService.register(email, password)
        if response:
            st.success("Registered successfully! Please log in.")
        else:
            st.error("Registration failed!")

    def show_conversation_page(self) -> None:
        try:
            # Fetch the list of conversations
            conversations = ConversationService.get_conversations(
                st.session_state.token
            )

            if conversations:
                # Store the conversations into the session state
                st.session_state.conversations = conversations

                # Function to truncate titles
                def truncate_title(title, max_length=40):
                    return (
                        title
                        if len(title) <= max_length
                        else title[:max_length] + "..."
                    )

                # Display Conversations in sidebar
                st.sidebar.title("Conversations")

                # Button to create a new conversation
                if st.sidebar.button("Create New Conversation"):
                    self.create_new_conversation()

                # Iterate over all conversations to display them
                for conv in conversations:
                    # Create a readable title with truncation if necessary
                    title = f"Conversation {conv['id']} ({conv['created_at']})"
                    truncated_title = truncate_title(title)

                    # Use a button for each truncated conversation to handle selection
                    if st.sidebar.button(truncated_title):
                        # Set the selected conversation ID
                        st.session_state.selected_conversation_id = conv["id"]

                # Load and display messages for the selected conversation
                if "selected_conversation_id" in st.session_state:
                    st.write(
                        f"Selected Conversation: {st.session_state.selected_conversation_id}"
                    )
                    self.load_messages()

                # Allow the user to send a message
                self.send_message()
            else:
                st.error("Failed to load conversations.")
        except Exception as ex:
            st.error("An error occurred while loading conversations.")
            logger.error(f"Exception: {ex}")

    def create_new_conversation(self) -> None:
        try:
            response = ConversationService.create_conversation(st.session_state.token)
            if response:
                st.success("New conversation created successfully!")
                st.rerun()  # Refresh to update the conversation list
            else:
                st.error("Failed to create a new conversation.")
        except Exception as ex:
            st.error("An error occurred while creating a new conversation.")
            logger.error(f"Exception: {ex}")

    def load_messages(self) -> None:
        if "selected_conversation_id" in st.session_state:
            try:
                # Fetch messages using the ConversationService
                messages = ConversationService.get_messages(
                    st.session_state.token, st.session_state.selected_conversation_id
                )
                if messages:
                    # Implement CSS for fixed layout
                    st.markdown(
                        """
                        <style>
                        .message-box {
                            border-radius: 8px;
                            padding: 10px;
                            margin-bottom: 10px;
                            box-shadow: 1px 1px 5px rgba(0, 0, 0, 0.1);
                        }
                        .message-container {
                            max-height: 400px; /* Adjust as needed */
                            overflow-y: auto;
                            margin-bottom: 20px;
                        }
                        </style>
                        """,
                        unsafe_allow_html=True,
                    )
                    st.write("Messages:")
                    # Wrap messages in a scrollable container
                    st.markdown(
                        '<div class="message-container">', unsafe_allow_html=True
                    )

                    # Reverse the order of messages for display
                    for message in reversed(messages["messages"]):
                        # Set border color based on role
                        if message["role"] == "user":
                            border_color = "#0288d1"  # Blue for user messages
                        elif message["role"] == "assistant":
                            border_color = "#7cb342"  # Green for assistant messages
                        else:
                            border_color = "#c2185b"  # Pink for other roles

                        # Join content of each message for display
                        content = " ".join(message["content"])
                        message_html = f"""
                        <div class="message-box" style="border: 2px solid {border_color};">
                            <strong>{message['role']}:</strong> {content}
                        </div>
                        """
                        # Use st.markdown with unsafe_allow_html=True to render each message
                        st.markdown(message_html, unsafe_allow_html=True)
                    # Close the scrollable message container
                    st.markdown("</div>", unsafe_allow_html=True)
                else:
                    st.error("Failed to load messages.")
            except Exception as ex:
                st.error("An error occurred while loading messages.")
                logger.error(f"Exception: {ex}")

    def send_message(self) -> None:
        new_message = st.text_input(
            "Your message:", placeholder="Type your message here...", key="new_message"
        )

        if st.button("Send"):
            try:
                response = ConversationService.send_message(
                    st.session_state.token,
                    st.session_state.selected_conversation_id,
                    new_message,  # Use the session state value
                )
                if response:
                    st.rerun()
                else:
                    st.error("Failed to send message.")
            except Exception as ex:
                st.error("An error occurred while sending the message.")
                logger.error(f"Exception: {ex}")


if __name__ == "__main__":
    app = ChatApp()
    app.run()
