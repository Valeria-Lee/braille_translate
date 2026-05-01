from sqlalchemy import String, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database.connection import Base

class User(Base):
    __tablename__ = "users"

    id:         Mapped[int]      = mapped_column(primary_key=True)
    email:      Mapped[str]      = mapped_column(String(255), unique=True, nullable=False)
    password:   Mapped[str]      = mapped_column(String(255), nullable=False)
    created_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now())

    device:     Mapped["Device"]      = relationship("Device", back_populates="user", uselist=False)
    documents:  Mapped[list["Document"]]   = relationship("Document", back_populates="user")
    braille_logs: Mapped[list["BrailleLog"]] = relationship("BrailleLog", back_populates="user")
    intent_logs:  Mapped[list["IntentLog"]]  = relationship("IntentLog", back_populates="user")