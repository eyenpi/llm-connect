from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from werkzeug.security import generate_password_hash, check_password_hash
from app.src.db import Base
from typing import Any


class User(Base):
    __tablename__ = "users"

    id: int = Column(Integer, primary_key=True)
    email: str = Column(String(120), unique=True, nullable=False)
    password_hash: str = Column(String(255), nullable=False)
    created_at: datetime = Column(DateTime, default=datetime.now(timezone.utc))

    # Relationship to ConversationThread
    threads = relationship("ConversationThread", back_populates="user")

    def set_password(self, password: str) -> None:
        """Hashes and sets the user's password."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        """Checks if the provided password matches the hashed password."""
        return check_password_hash(self.password_hash, password)

    def __repr__(self) -> str:
        """Provides a string representation of the User object."""
        return f"<User(email={self.email})>"
