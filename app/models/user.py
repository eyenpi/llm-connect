from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from werkzeug.security import generate_password_hash, check_password_hash
from app.src.db import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String(120), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationship to ConversationThread
    threads = relationship("ConversationThread", back_populates="user")

    def set_password(self, password):
        """Hashes and sets the user's password."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Checks if the provided password matches the hashed password."""
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<User {self.email}>"
