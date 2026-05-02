from sqlalchemy import String, Text, Float, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database.connection import Base

class Document(Base):
    __tablename__ = "documents"

    id:               Mapped[int]   = mapped_column(primary_key=True)
    user_id:          Mapped[int]   = mapped_column(ForeignKey("users.id"), nullable=False)
    title:            Mapped[str]   = mapped_column(String(255), nullable=False)
    author:           Mapped[str]   = mapped_column(String(255), nullable=True)
    file_path:        Mapped[str]   = mapped_column(String(500), nullable=False)
    file_type:        Mapped[str]   = mapped_column(String(10), nullable=False) # pdf / epub / docx
    reading_progress: Mapped[float] = mapped_column(Float, default=0.0)
    last_read_at:     Mapped[DateTime] = mapped_column(DateTime, nullable=True)
    added_at:         Mapped[DateTime] = mapped_column(DateTime, server_default=func.now())

    user:         Mapped["User"]          = relationship("User", back_populates="documents")
    braille_logs: Mapped[list["BrailleLog"]] = relationship("BrailleLog", back_populates="document")