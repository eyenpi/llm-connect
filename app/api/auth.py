import jwt
import os
import datetime
from functools import wraps
from flask import request, jsonify
from app.src.db import get_db
from app.models.user import User
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = str(os.getenv("SECRET_KEY"))


def generate_token(user_id):
    payload = {
        "user_id": str(user_id),
        "exp": datetime.datetime.now(datetime.timezone.utc)
        + datetime.timedelta(hours=1),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get("Authorization")

        if not token:
            return jsonify({"error": "Token is missing!"}), 401

        try:
            if token.startswith("Bearer "):
                token = token.split()[1]

            data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            user_id = data["user_id"]

            db = next(get_db())
            current_user = db.query(User).filter_by(id=user_id).first()
            if not current_user:
                return jsonify({"error": "User not found!"}), 404

        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token has expired!"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token!"}), 401

        return f(current_user=current_user, *args, **kwargs)

    return decorated


def authenticate_user(email, password):
    db = next(get_db())
    user = db.query(User).filter_by(email=email).first()
    if user and user.check_password(password):
        return user
    return None
