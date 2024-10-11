import datetime
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.src.db import Base


class ConversationThread(Base):
    __tablename__ = "conversation_threads"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    thread_id = Column(String(120), unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.now(datetime.timezone.utc))
    assistant_id = Column(String(120), nullable=True)
    status = Column(String(50), default="active")

    user = relationship("User", back_populates="threads")

    def __repr__(self):
        return f"<ConversationThread {self.thread_id} for User {self.user_id}>"
