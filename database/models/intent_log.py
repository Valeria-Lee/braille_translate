from sqlalchemy import String, Float, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database.connection import Base

class IntentLog(Base):
    __tablename__ = "intent_logs"

    id:         Mapped[int]   = mapped_column(primary_key=True)
    user_id:    Mapped[int]   = mapped_column(ForeignKey("users.id"), nullable=False)
    query:      Mapped[str]   = mapped_column(String, nullable=False)
    intent:     Mapped[str]   = mapped_column(String(50), nullable=False)
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    created_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now())

    user: Mapped["User"] = relationship("User", back_populates="intent_logs")