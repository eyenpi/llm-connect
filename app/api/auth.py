import jwt
import os
import datetime
from functools import wraps
from flask import request, jsonify
from sqlalchemy.orm import Session
from app.src.db import get_db
from app.models.user import User
from dotenv import load_dotenv
from typing import Callable, Any, Optional, Dict

load_dotenv()

# Ensure the SECRET_KEY is properly loaded
SECRET_KEY = os.getenv("JWT_SECRET")
if not SECRET_KEY:
    raise ValueError("No SECRET_KEY set for Flask application.")


def generate_token(user_id: int) -> str:
    """Generates a JWT token for a user."""
    payload = {
        "user_id": str(user_id),
        "exp": datetime.datetime.now(datetime.timezone.utc)
        + datetime.timedelta(hours=1),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")


def token_required(f: Callable) -> Callable:
    """Decorator to protect routes with token-based authentication."""

    @wraps(f)
    def decorated(*args: Any, **kwargs: Any) -> Any:
        token: Optional[str] = request.cookies.get("token")
        if not token:
            return jsonify({"error": "Token is missing!"}), 401

        try:
            data: Dict[str, Any] = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            user_id: str = data["user_id"]

            db: Session = next(get_db())
            current_user: Optional[User] = db.query(User).filter_by(id=user_id).first()

            if not current_user:
                return jsonify({"error": "User not found!"}), 404

        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token has expired!"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token!"}), 401

        return f(current_user=current_user, *args, **kwargs)

    return decorated


def authenticate_user(email: str, password: str) -> Optional[User]:
    """Authenticates a user by their email and password."""
    db: Session = next(get_db())
    user: Optional[User] = db.query(User).filter_by(email=email).first()

    if user and user.check_password(password):
        return user

    return None
