from flask import Flask, request, jsonify
from app.src.db import get_db
from app.models.user import User
from app.models.conversation_thread import ConversationThread
from app.api.auth import token_required, authenticate_user, generate_token
import logging

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


@app.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"error": "Email and password are required."}), 400

    db = next(get_db())

    # Check if a user with the same email already exists
    existing_user = db.query(User).filter_by(email=email).first()

    if existing_user:
        return jsonify({"error": "User with this email already exists."}), 400

    try:
        new_user = User(email=email)
        new_user.set_password(password)

        db.add(new_user)
        db.commit()
    except Exception as e:
        logger.error(f"Error registering user: {e}")
        return jsonify({"error": "An error occurred while registering the user."}), 500

    logger.info(f"User registered with email: {email}")
    return jsonify({"message": "User registered successfully."}), 201


@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    user = authenticate_user(email, password)
    if user:
        token = generate_token(user.id)
        return jsonify({"token": token})

    return jsonify({"error": "Invalid credentials"}), 401


@app.route("/user", methods=["GET"])
@token_required
def get_user_info(current_user):
    return jsonify({"id": current_user.id, "email": current_user.email})


@app.route("/conversations", methods=["POST"])
@token_required
def create_conversation(current_user):
    data = request.get_json()
    title = data.get("title")

    db = next(get_db())
    new_thread = ConversationThread(title=title, user_id=current_user.id)
    db.add(new_thread)
    db.commit()

    return jsonify({"message": "Conversation created", "thread_id": new_thread.id})


@app.route("/conversations", methods=["GET"])
@token_required
def list_conversations(current_user):
    db = next(get_db())
    threads = db.query(ConversationThread).filter_by(user_id=current_user.id).all()

    return jsonify([{"id": thread.id, "title": thread.title} for thread in threads])


@app.route("/")
def index():
    return "Welcome to LLM Connect!"


if __name__ == "__main__":
    app.run(debug=True)
