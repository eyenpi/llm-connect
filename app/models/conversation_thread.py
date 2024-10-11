from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.src.db import Base
from typing import Optional


class ConversationThread(Base):
    __tablename__ = "conversation_threads"

    id: int = Column(Integer, primary_key=True)
    user_id: int = Column(Integer, ForeignKey("users.id"), nullable=False)
    thread_id: str = Column(String(120), unique=True, nullable=False)
    created_at: datetime = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    assistant_id: Optional[str] = Column(String(120), nullable=True)
    status: str = Column(String(50), default="active")

    user = relationship("User", back_populates="threads")

    def __repr__(self) -> str:
        """Provides a string representation of the ConversationThread object."""
        return (
            f"<ConversationThread(thread_id={self.thread_id}, user_id={self.user_id})>"
        )
