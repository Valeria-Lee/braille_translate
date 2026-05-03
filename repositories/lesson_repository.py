from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from database.models.lesson import Lesson, LessonBlock, Question, UserLessonProgress
from datetime import datetime
import json

async def get_all_lessons(db: AsyncSession) -> list[Lesson]:
    result = await db.execute(select(Lesson).order_by(Lesson.order))
    return result.scalars().all()

async def get_lesson_by_id(db: AsyncSession, lesson_id: int) -> Lesson | None:
    result = await db.execute(
        select(Lesson)
        .where(Lesson.id == lesson_id)
        .options(
            selectinload(Lesson.blocks),
            selectinload(Lesson.questions)
        )
    )
    return result.scalar_one_or_none()

async def get_user_progress(db: AsyncSession, user_id: int) -> list[UserLessonProgress]:
    result = await db.execute(
        select(UserLessonProgress).where(UserLessonProgress.user_id == user_id)
    )
    return result.scalars().all()

async def save_progress(
    db: AsyncSession,
    user_id: int,
    lesson_id: int,
    score: float
) -> UserLessonProgress:
    # if progress already exists
    result = await db.execute(
        select(UserLessonProgress).where(
            UserLessonProgress.user_id == user_id,
            UserLessonProgress.lesson_id == lesson_id
        )
    )
    progress = result.scalar_one_or_none()

    if progress:
        progress.completed = True
        progress.score = score
        progress.completed_at = datetime.now()
    else:
        progress = UserLessonProgress(
            user_id=user_id,
            lesson_id=lesson_id,
            completed=True,
            score=score,
            completed_at=datetime.now()
        )
        db.add(progress)

    await db.commit()
    await db.refresh(progress)
    return progress

# admin
async def create_lesson(db: AsyncSession, title: str, description: str, order: int) -> Lesson:
    lesson = Lesson(title=title, description=description, order=order)
    db.add(lesson)
    await db.commit()
    await db.refresh(lesson)
    return lesson

async def create_block(
    db: AsyncSession,
    lesson_id: int,
    order: int,
    type: str,
    content: str,
    braille_text: str | None = None
) -> LessonBlock:
    block = LessonBlock(
        lesson_id=lesson_id,
        order=order,
        type=type,
        content=content,
        braille_text=braille_text
    )
    db.add(block)
    await db.commit()
    await db.refresh(block)
    return block

async def create_question(
    db: AsyncSession,
    lesson_id: int,
    order: int,
    type: str,
    question: str,
    options: list | None,
    correct_answer: str
) -> Question:
    q = Question(
        lesson_id=lesson_id,
        order=order,
        type=type,
        question=question,
        options=json.dumps(options) if options else None,
        correct_answer=correct_answer
    )
    db.add(q)
    await db.commit()
    await db.refresh(q)
    return q