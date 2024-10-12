from flask import Flask, request, jsonify, make_response
from sqlalchemy.orm import Session
from app.src.db import get_db
from app.models.user import User
from app.models.conversation_thread import ConversationThread
from app.api.auth import token_required, authenticate_user, generate_token
import logging
from typing import Iterator, Dict, Any
from http import HTTPStatus
from app.assistants.openai import OpenAIAssistant

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

openai_client = OpenAIAssistant()


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
        logger.warning("Missing email or password in JSON data")
        return (
            jsonify({"error": "Email and password are required"}),
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
    data = request.get_json()
    if not data:
        logger.warning("Empty JSON request body")
        return jsonify({"error": "Request body must be JSON"}), HTTPStatus.BAD_REQUEST

    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        logger.warning("Missing email or password in JSON data")
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
            secure=False,  # TODO: Set to True in production for HTTPS
            samesite="Lax",
        )

        return response

    logger.warning(f"Invalid login attempt for email: {email}")
    return jsonify({"error": "Invalid credentials"}), HTTPStatus.UNAUTHORIZED


@app.route("/user", methods=["GET"])
@token_required
def get_user_info(current_user: User) -> Dict[str, Any]:
    logger.info(f"User info retrieved for user ID: {current_user.id}")
    return jsonify({"id": current_user.id, "email": current_user.email}), HTTPStatus.OK


@app.route("/conversations", methods=["POST"])
@token_required
def create_conversation(current_user: User) -> Dict[str, Any]:

    thread_id = openai_client.create_thread()
    if not thread_id:
        logger.error("Error creating conversation thread")
        return (
            jsonify({"error": "An error occurred creating the conversation thread"}),
            HTTPStatus.INTERNAL_SERVER_ERROR,
        )

    assistant_id = openai_client.get_assistant_id()
    if not assistant_id:
        logger.error("Error getting assistant ID")
        return (
            jsonify({"error": "An error occurred getting the assistant ID"}),
            HTTPStatus.INTERNAL_SERVER_ERROR,
        )

    new_conversation = ConversationThread(
        user_id=current_user.id,
        thread_id=thread_id,
        assistant_id=assistant_id,
    )
    db_session = next(get_database_session())
    db_session.add(new_conversation)
    db_session.commit()
    logger.info(f"Conversation thread created with ID: {new_conversation.id}")

    return (
        jsonify(
            {"message": "Conversation created", "conversation_id": new_conversation.id}
        ),
        HTTPStatus.CREATED,
    )


@app.route("/conversations", methods=["GET"])
@token_required
def list_conversations(current_user: User) -> Dict[str, Any]:
    db_session = next(get_database_session())
    conversations = (
        db_session.query(ConversationThread).filter_by(user_id=current_user.id).all()
    )
    logger.info(f"Conversations listed for user ID: {current_user.id}")
    return (
        jsonify(
            [
                {
                    "id": conversation.id,
                    "thread_id": conversation.thread_id,
                    "assistant_id": conversation.assistant_id,
                    "created_at": conversation.created_at,
                    "status": conversation.status,
                }
                for conversation in conversations
            ]
        ),
        HTTPStatus.OK,
    )


@app.route("/conversations/<int:conversation_id>/messages", methods=["POST"])
@token_required
def send_message(current_user: User, conversation_id: int) -> Dict[str, Any]:
    data = request.get_json()
    if not data:
        logger.warning("Empty JSON request body")
        return jsonify({"error": "Request body must be JSON"}), HTTPStatus.BAD_REQUEST

    message = data.get("message")
    if not message:
        logger.warning("Message missing in request body")
        return jsonify({"error": "Message is required"}), HTTPStatus.BAD_REQUEST

    db_session = next(get_database_session())
    conversation = (
        db_session.query(ConversationThread)
        .filter_by(id=conversation_id, user_id=current_user.id)
        .first()
    )

    if not conversation:
        logger.warning(
            f"Conversation {conversation_id} not found for user {current_user.id}"
        )
        return jsonify({"error": "Conversation not found"}), HTTPStatus.NOT_FOUND

    openai_response = openai_client.send_message(
        thread_id=conversation.thread_id,
        assistant_id=conversation.assistant_id,
        message=message,
    )

    if not openai_response:
        logger.error("Error sending message to OpenAI")
        return (
            jsonify({"error": "An error occurred sending the message"}),
            HTTPStatus.INTERNAL_SERVER_ERROR,
        )

    logger.info(f"Message sent to conversation {conversation_id}")
    return jsonify(openai_response), HTTPStatus.OK


@app.route("/conversations/<int:conversation_id>/messages", methods=["GET"])
@token_required
def get_conversation_messages(
    conversation_id: str, current_user: User
) -> Dict[str, Any]:
    try:
        db_session = next(get_database_session())
        conversation = (
            db_session.query(ConversationThread)
            .filter_by(id=conversation_id, user_id=current_user.id)
            .first()
        )

        if not conversation:
            logger.warning(
                f"Conversation with ID {conversation_id} not found for user {current_user.id}"
            )
            return jsonify({"error": "Conversation not found"}), HTTPStatus.NOT_FOUND

        # Fetch the thread messages from OpenAI
        messages = openai_client.get_thread_messages(conversation.thread_id)

        if not messages and not isinstance(messages, list):
            logger.error("Error fetching conversation messages")
            return (
                jsonify(
                    {"error": "An error occurred fetching the conversation messages"}
                ),
                HTTPStatus.INTERNAL_SERVER_ERROR,
            )

        return (
            jsonify(
                {
                    "conversation_id": conversation_id,
                    "messages": messages,
                }
            ),
            HTTPStatus.OK,
        )

    except Exception as e:
        logger.error(
            f"Error fetching conversation messages for {conversation_id}: {str(e)}"
        )
        return (
            jsonify({"error": "Failed to retrieve conversation messages"}),
            HTTPStatus.INTERNAL_SERVER_ERROR,
        )


@app.route("/conversations/<int:conversation_id>/thread", methods=["GET"])
@token_required
def get_conversation_thread(conversation_id: int, current_user: User) -> Dict[str, Any]:
    try:
        db_session = next(get_database_session())
        conversation = (
            db_session.query(ConversationThread)
            .filter_by(id=conversation_id, user_id=current_user.id)
            .first()
        )

        if not conversation:
            logger.warning(
                f"Conversation with ID {conversation_id} not found for user {current_user.id}"
            )
            return jsonify({"error": "Conversation not found"}), HTTPStatus.NOT_FOUND

        # Fetch the thread messages from OpenAI
        thread = openai_client.get_thread(conversation.thread_id).to_json()

        if not thread:
            logger.error("Error fetching conversation thread messages")
            return (
                jsonify(
                    {"error": "An error occurred fetching the conversation thread"}
                ),
                HTTPStatus.INTERNAL_SERVER_ERROR,
            )

        return (
            jsonify(
                {
                    "conversation_id": conversation_id,
                    "thread_id": conversation.thread_id,
                    "content": thread,
                }
            ),
            HTTPStatus.OK,
        )

    except Exception as e:
        logger.error(
            f"Error fetching conversation thread for {conversation_id}: {str(e)}"
        )
        return (
            jsonify({"error": "Failed to retrieve conversation thread"}),
            HTTPStatus.INTERNAL_SERVER_ERROR,
        )


@app.route("/")
def index() -> str:
    logger.info("Index page accessed")
    return "Welcome to LLM Connect!"


if __name__ == "__main__":
    app.run(debug=True)
    # fapp = ChatApp()
    # fapp.run()
