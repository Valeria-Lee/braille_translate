from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from database.connection import get_db
from database.models.user import User
from auth.dependencies import get_current_user
from repositories.lesson_repository import (
    get_all_lessons,
    get_lesson_by_id,
    get_user_progress,
    save_progress,
    create_lesson,
    create_block,
    create_question
)
from utils.braille_translation import braille_translate, send_braille_characters
from utils.device import braille_device
import json
from difflib import SequenceMatcher

router = APIRouter(prefix="/learn", tags=["learn"])

# all lessons with user progress
@router.get("/lessons")
async def get_lessons(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    lessons = await get_all_lessons(db)
    progress = await get_user_progress(db, current_user.id)
    progress_map = {p.lesson_id: p for p in progress}

    return [
        {
            "id": l.id,
            "title": l.title,
            "description": l.description,
            "order": l.order,
            "completed": progress_map.get(l.id, None) is not None and progress_map[l.id].completed,
            "score": progress_map[l.id].score if l.id in progress_map else None
        }
        for l in lessons
    ]

# full lesson with blocks and questions
@router.get("/lessons/{lesson_id}")
async def get_lesson(
    lesson_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    lesson = await get_lesson_by_id(db, lesson_id)
    if not lesson:
        raise HTTPException(status_code=404, detail="Lección no encontrada")

    return {
        "id": lesson.id,
        "title": lesson.title,
        "description": lesson.description,
        "blocks": [
            {
                "id": b.id,
                "order": b.order,
                "type": b.type,
                "content": b.content,
                "braille_text": b.braille_text
            }
            for b in lesson.blocks
        ],
        "questions": [
            {
                "id": q.id,
                "order": q.order,
                "type": q.type,
                "question": q.question,
                "options": json.loads(q.options) if q.options else None
                # correct_answer NOT sent to client
            }
            for q in lesson.questions
        ]
    }

# send braille text to device
@router.post("/render")
async def render_to_device(
    text: str,
    current_user: User = Depends(get_current_user)
):
    if not braille_device.is_connected:
        raise HTTPException(status_code=503, detail="Dispositivo no conectado")

    braille_data = braille_translate(text)
    dots = send_braille_characters(braille_data)
    ok = await braille_device.load_text(dots)

    return {
        "ok": ok,
        "total_lines": braille_device.total_lines
    }

def respuesta_correcta(transcribed: str, correct: str) -> bool:
    t = transcribed.lower().strip()
    c = correct.lower().strip()
    
    if t == c:
        return True
    if c in t:
        return True
    
    ratio = SequenceMatcher(None, t, c).ratio()
    return ratio >= 0.80

# save progress and score
class CompleteRequest(BaseModel):
    answers: dict  # {question_id: answer}

@router.post("/lessons/{lesson_id}/complete")
async def complete_lesson(
    lesson_id: int,
    req: CompleteRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    lesson = await get_lesson_by_id(db, lesson_id)
    if not lesson:
        raise HTTPException(status_code=404, detail="Lección no encontrada")

    # calculate score
    total = len(lesson.questions)
    if total == 0:
        score = 1.0
    else:
        correct = sum(
            1 for q in lesson.questions
            if respuesta_correcta(
                str(req.answers.get(str(q.id), "")),
                q.correct_answer
            )
        )
        score = correct / total

    progress = await save_progress(db, current_user.id, lesson_id, score)

    return {
        "ok": True,
        "score": score,
        "completed_at": progress.completed_at
    }


class LessonCreate(BaseModel):
    title: str
    description: str | None = None
    order: int = 0

class BlockCreate(BaseModel):
    order: int
    type: str
    content: str
    braille_text: str | None = None

class QuestionCreate(BaseModel):
    order: int
    type: str
    question: str
    options: list | None = None
    correct_answer: str

@router.post("/admin/lessons")
async def admin_create_lesson(
    req: LessonCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # TODO: add admin role check when roles are implemented
    lesson = await create_lesson(db, req.title, req.description, req.order)
    return {"id": lesson.id, "title": lesson.title}

@router.post("/admin/lessons/{lesson_id}/blocks")
async def admin_create_block(
    lesson_id: int,
    req: BlockCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    block = await create_block(
        db, lesson_id, req.order, req.type, req.content, req.braille_text
    )
    return {"id": block.id, "order": block.order}

@router.post("/admin/lessons/{lesson_id}/questions")
async def admin_create_question(
    lesson_id: int,
    req: QuestionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    question = await create_question(
        db, lesson_id, req.order, req.type,
        req.question, req.options, req.correct_answer
    )
    return {"id": question.id, "order": question.order}