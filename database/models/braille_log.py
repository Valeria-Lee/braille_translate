from sqlalchemy import String, Integer, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database.connection import Base

class BrailleLog(Base):
    __tablename__ = "braille_logs"

    id:          Mapped[int] = mapped_column(primary_key=True)
    user_id:     Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    document_id: Mapped[int] = mapped_column(ForeignKey("documents.id"), nullable=True)
    text:        Mapped[str] = mapped_column(String, nullable=False)
    total_lines: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at:  Mapped[DateTime] = mapped_column(DateTime, server_default=func.now())

    user:     Mapped["User"]     = relationship("User", back_populates="braille_logs")
    document: Mapped["Document"] = relationship("Document", back_populates="braille_logs")