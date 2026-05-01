from sqlalchemy import String, Integer, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database.connection import Base

class Device(Base):
    __tablename__ = "devices"

    id:             Mapped[int] = mapped_column(primary_key=True)
    user_id:        Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True, nullable=False)
    device_token:   Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    cells:          Mapped[int] = mapped_column(Integer, default=1)
    last_connected: Mapped[DateTime] = mapped_column(DateTime, nullable=True)

    user: Mapped["User"] = relationship("User", back_populates="device")