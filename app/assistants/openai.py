import os
import logging
from openai import OpenAI
from dotenv import load_dotenv
from typing import Optional, Dict, Any

# Load environment variables from .env
load_dotenv()

# Set up logging configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("app.log"),  # Logs to a file
        logging.StreamHandler(),  # Also logs to the console
    ],
)
logger = logging.getLogger(__name__)


class OpenAIAssistant:
    def __init__(self) -> None:
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            logger.error("OpenAI API key not set in environment variables.")
            raise ValueError("The OpenAI API key is not set.")

        logger.info("OpenAI API key successfully loaded.")
        self.client = OpenAI(api_key=self.api_key)

    def get_assistant_id(self) -> Optional[str]:
        """Return a fixed assistant ID (hardcoded)."""
        assistant_id = "asst_Bd6nPv9qhFDPR74IuN2jOokL"
        logger.info(f"Returning assistant ID: {assistant_id}")
        return assistant_id

    def create_thread(self) -> Optional[str]:
        """Creates a conversation thread in OpenAI."""
        try:
            logger.info("Creating a new conversation thread.")
            thread = self.client.beta.threads.create()
            logger.info(f"Conversation thread created with ID: {thread.id}")
            return thread.id
        except Exception as e:
            logger.error(f"Failed to create conversation thread: {e}")
            return None

    def send_message(
        self, thread_id: str, assistant_id: str, message: str
    ) -> Optional[Dict[str, str]]:
        """Sends a message to the assistant in a specific conversation thread."""
        try:
            logger.info(
                f"Sending message to thread {thread_id} with assistant {assistant_id}."
            )
            message_response = self.client.beta.threads.messages.create(
                thread_id=thread_id,
                role="user",
                content=message,
            )
            logger.info(f"Message sent: {message}")

            # Wait for the assistant to respond
            run_response = self.client.beta.threads.runs.create_and_poll(
                thread_id=thread_id,
                assistant_id=assistant_id,
            )

            if run_response.status == "completed":
                logger.info(f"Assistant response completed for thread {thread_id}.")
                messages = self.client.beta.threads.messages.list(thread_id=thread_id)
                # assistant_reply = (
                #     messages[-1].content if messages else "No response from assistant."
                # )
                assistant_reply = messages
                logger.info(f"Assistant response: {assistant_reply}")
                return self._extract_last_message(assistant_reply)
            else:
                logger.error(
                    f"Assistant did not complete the response for thread {thread_id}. Status: {run_response.status}"
                )
                return None

        except Exception as e:
            logger.error(
                f"Error sending message to thread {thread_id} with assistant {assistant_id}: {e}"
            )
            return None

    def _extract_last_message(self, response: Dict[str, Any]) -> Optional[str]:
        try:
            messages = response.data
            if not messages:
                logger.warning("No messages found.")
                return None

            for message in reversed(messages):
                if message.role == "assistant":
                    content = message.content[0].text.value
                    return content

            logger.info("No assistant message found.")
            return None

        except Exception as e:
            logger.error(f"Error extracting last assistant message: {e}")
            return None

    def get_thread_messages(self, thread_id: str) -> Optional[Dict[str, Any]]:
        """Fetches all messages in a conversation thread."""
        try:
            messages = self.client.beta.threads.messages.list(thread_id=thread_id)
            thread_data = []
            for message in messages.data:
                message_data = {
                    "id": message.id,
                    "role": message.role,
                    "created_at": message.created_at,
                    "content": [
                        content_block.text.value for content_block in message.content
                    ],
                }
                thread_data.append(message_data)

            logger.info(f"Fetched {len(thread_data)} messages for thread {thread_id}.")
            return thread_data
        except Exception as e:
            logger.error(f"Error fetching messages for thread {thread_id}: {e}")
            return None

    def get_thread(self, thread_id: str) -> Optional[Dict[str, Any]]:
        """Fetches a conversation thread by ID."""
        try:
            thread = self.client.beta.threads.retrieve(thread_id)
            logger.info(f"Fetched conversation thread with ID: {thread_id}")
            return thread
        except Exception as e:
            logger.error(f"Error fetching conversation thread {thread_id}: {e}")
            return None
