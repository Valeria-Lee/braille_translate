from sqlalchemy import String, Text, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database.connection import Base

class Document(Base):
    __tablename__ = "documents"

    id:         Mapped[int] = mapped_column(primary_key=True)
    user_id:    Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    title:      Mapped[str] = mapped_column(String(255), nullable=False)
    content:    Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now())

    user: Mapped["User"] = relationship("User", back_populates="documents")
    braille_logs: Mapped[list["BrailleLog"]] = relationship("BrailleLog", back_populates="document")