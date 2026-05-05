from sqlalchemy import String, Text, Integer, Boolean, Float, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database.connection import Base

class Lesson(Base):
    __tablename__ = "lessons"

    id:          Mapped[int] = mapped_column(primary_key=True)
    title:       Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    order:       Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at:  Mapped[DateTime] = mapped_column(DateTime, server_default=func.now())

    blocks:   Mapped[list["LessonBlock"]]         = relationship("LessonBlock", back_populates="lesson", order_by="LessonBlock.order")
    questions: Mapped[list["Question"]]           = relationship("Question", back_populates="lesson", order_by="Question.order")
    progress:  Mapped[list["UserLessonProgress"]] = relationship("UserLessonProgress", back_populates="lesson")


class LessonBlock(Base):
    __tablename__ = "lesson_blocks"

    id:           Mapped[int] = mapped_column(primary_key=True)
    lesson_id:    Mapped[int] = mapped_column(ForeignKey("lessons.id"), nullable=False)
    order:        Mapped[int] = mapped_column(Integer, nullable=False)
    type:         Mapped[str] = mapped_column(String(20), nullable=False) # text / braille
    content:      Mapped[str] = mapped_column(Text, nullable=False) # text to show/hear
    braille_text: Mapped[str] = mapped_column(String(255), nullable=True) # what to send to device

    lesson: Mapped["Lesson"] = relationship("Lesson", back_populates="blocks")


class Question(Base):
    __tablename__ = "questions"

    id:             Mapped[int] = mapped_column(primary_key=True)
    lesson_id:      Mapped[int] = mapped_column(ForeignKey("lessons.id"), nullable=False)
    order:          Mapped[int] = mapped_column(Integer, nullable=False)
    type:           Mapped[str] = mapped_column(String(20), nullable=False) # multiple_choice / true_false
    question:       Mapped[str] = mapped_column(Text, nullable=False)
    options:        Mapped[str] = mapped_column(Text, nullable=True)
    correct_answer: Mapped[str] = mapped_column(String(255), nullable=False)

    lesson: Mapped["Lesson"] = relationship("Lesson", back_populates="questions")


class UserLessonProgress(Base):
    __tablename__ = "user_lesson_progress"

    id:           Mapped[int]   = mapped_column(primary_key=True)
    user_id:      Mapped[int]   = mapped_column(ForeignKey("users.id"), nullable=False)
    lesson_id:    Mapped[int]   = mapped_column(ForeignKey("lessons.id"), nullable=False)
    completed:    Mapped[bool]  = mapped_column(Boolean, default=False)
    score:        Mapped[float] = mapped_column(Float, nullable=True)
    last_block_id: Mapped[int]  = mapped_column(Integer, nullable=True)
    completed_at: Mapped[DateTime] = mapped_column(DateTime, nullable=True)

    user:   Mapped["User"]   = relationship("User")
    lesson: Mapped["Lesson"] = relationship("Lesson", back_populates="progress")