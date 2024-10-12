import requests
from typing import Dict, Any, Optional
from frontend.utils.logger import setup_logger
from dotenv import load_dotenv
import os

logger = setup_logger(__name__)
load_dotenv()


class AuthService:
    BASE_URL = os.getenv("BACKEND_URL")

    @classmethod
    def register(cls, email: str, password: str) -> Optional[Dict[str, Any]]:
        try:
            response = requests.post(
                f"{cls.BASE_URL}/register", json={"email": email, "password": password}
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Registration failed: {e}")
            return None

    @classmethod
    def login(cls, email: str, password: str) -> Optional[str]:
        try:
            response = requests.post(
                f"{cls.BASE_URL}/login", json={"email": email, "password": password}
            )
            response.raise_for_status()
            token = response.cookies.get("token")
            return token
        except requests.RequestException as e:
            logger.error(f"Login failed: {e}")
            return None
