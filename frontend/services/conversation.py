import requests
from typing import Dict, Any, Optional
from frontend.utils.logger import setup_logger
from dotenv import load_dotenv
import os

logger = setup_logger(__name__)
load_dotenv()


class ConversationService:
    BASE_URL = os.getenv("BACKEND_URL")

    @classmethod
    def get_conversations(cls, token: str) -> Optional[Dict[str, Any]]:
        # Set token as 'token' in the cookies
        cookies = {"token": token}
        try:
            response = requests.get(f"{cls.BASE_URL}/conversations", cookies=cookies)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Fetching conversations failed: {e}")
            return None

    @classmethod
    def create_conversation(cls, token: str) -> Optional[Dict[str, Any]]:
        # Set token as 'token' in the cookies
        cookies = {"token": token}
        try:
            response = requests.post(f"{cls.BASE_URL}/conversations", cookies=cookies)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Creating conversation failed: {e}")
            return None

    @classmethod
    def get_messages(cls, token: str, conversation_id: str) -> Optional[Dict[str, Any]]:
        # Set token as 'token' in the cookies
        cookies = {"token": token}
        try:
            response = requests.get(
                f"{cls.BASE_URL}/conversations/{conversation_id}/messages",
                cookies=cookies,
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Fetching messages failed: {e}")
            return None

    @classmethod
    def send_message(
        cls, token: str, conversation_id: str, message: str
    ) -> Optional[Dict[str, Any]]:
        # Set token as 'token' in the cookies
        cookies = {"token": token}
        try:
            response = requests.post(
                f"{cls.BASE_URL}/conversations/{conversation_id}/messages",
                json={"message": message},
                cookies=cookies,
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Sending message failed: {e}")
            return None
