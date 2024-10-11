from flask import Flask, request, jsonify, make_response
from sqlalchemy.orm import Session
from app.src.db import get_db
from app.models.user import User
from app.models.conversation_thread import ConversationThread
from app.api.auth import token_required, authenticate_user, generate_token
import logging
from typing import Iterator, Dict, Any
from http import HTTPStatus

app = Flask(__name__)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("app.log"),  # Logs to a file
        logging.StreamHandler(),  # Also logs to the console
    ],
)
logger = logging.getLogger(__name__)


def get_database_session() -> Iterator[Session]:
    db = next(get_db())
    try:
        yield db
    finally:
        db.close()


@app.route("/register", methods=["POST"])
def register() -> Dict[str, Any]:
    data = request.get_json()
    if not data:
        logger.warning("Empty JSON request body")
        return jsonify({"error": "Request body must be JSON"}), HTTPStatus.BAD_REQUEST

    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        logger.warning("Missing email or password")
        return (
            jsonify({"error": "Email and password are required."}),
            HTTPStatus.BAD_REQUEST,
        )

    db_session = next(get_database_session())

    if db_session.query(User).filter_by(email=email).first() is not None:
        logger.info(f"Attempt to register with existing email: {email}")
        return (
            jsonify({"error": "User with this email already exists."}),
            HTTPStatus.BAD_REQUEST,
        )

    try:
        new_user = User(email=email)
        new_user.set_password(password)
        db_session.add(new_user)
        db_session.commit()

        logger.info(f"User registered successfully with email: {email}")
        return jsonify({"message": "User registered successfully."}), HTTPStatus.CREATED

    except Exception as e:
        logger.error(f"Exception during registration: {str(e)}")
        return (
            jsonify({"error": "An error occurred registering the user."}),
            HTTPStatus.INTERNAL_SERVER_ERROR,
        )


@app.route("/login", methods=["POST"])
def login() -> Dict[str, Any]:
    email = request.form.get("email")
    password = request.form.get("password")

    if not email or not password:
        logger.warning("Missing email or password in form data")
        return (
            jsonify({"error": "Email and password are required"}),
            HTTPStatus.BAD_REQUEST,
        )

    user = authenticate_user(email, password)
    if user:
        token = generate_token(user.id)
        logger.info(f"User logged in: {email}")

        response = make_response(
            jsonify({"message": "Login successful"}), HTTPStatus.OK
        )

        response.set_cookie(
            key="token",
            value=token,
            httponly=True,
            secure=False,  # TODO: Set to True in production
            samesite="Lax",
        )

        return response

    logger.warning("Invalid login attempt for email: {email}")
    return jsonify({"error": "Invalid credentials"}), HTTPStatus.UNAUTHORIZED


@app.route("/user", methods=["GET"])
@token_required
def get_user_info(current_user: User) -> Dict[str, Any]:
    logger.info(f"User info retrieved for user ID: {current_user.id}")
    return jsonify({"id": current_user.id, "email": current_user.email}), HTTPStatus.OK


@app.route("/conversations", methods=["POST"])
@token_required
def create_conversation(current_user: User) -> Dict[str, Any]:
    data = request.get_json()
    if not data:
        logger.warning("Empty JSON request body")
        return jsonify({"error": "Request body must be JSON"}), HTTPStatus.BAD_REQUEST

    title = data.get("title")
    if not title:
        logger.warning("Title missing in request body")
        return jsonify({"error": "Title is required"}), HTTPStatus.BAD_REQUEST

    db_session = next(get_database_session())
    new_thread = ConversationThread(title=title, user_id=current_user.id)
    db_session.add(new_thread)
    db_session.commit()
    logger.info(f"Conversation thread created with ID: {new_thread.id}")

    return (
        jsonify({"message": "Conversation created", "thread_id": new_thread.id}),
        HTTPStatus.CREATED,
    )


@app.route("/conversations", methods=["GET"])
@token_required
def list_conversations(current_user: User) -> Dict[str, Any]:
    db_session = next(get_database_session())
    threads = (
        db_session.query(ConversationThread).filter_by(user_id=current_user.id).all()
    )
    logger.info(f"Conversations listed for user ID: {current_user.id}")
    return (
        jsonify([{"id": thread.id, "title": thread.title} for thread in threads]),
        HTTPStatus.OK,
    )


@app.route("/")
def index() -> str:
    logger.info("Index page accessed")
    return "Welcome to LLM Connect!"


if __name__ == "__main__":
    app.run(debug=True)
