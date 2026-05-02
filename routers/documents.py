from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from database.connection import get_db
from database.models.user import User
from auth.dependencies import get_current_user
from repositories.document_repository import (
    get_documents_by_user,
    get_document_by_id,
    create_document,
    update_reading_progress,
    delete_document
)
import os, shutil

router = APIRouter(prefix="/documentos", tags=["documentos"])

STORAGE_PATH = os.getenv("STORAGE_PATH")
ALLOWED_TYPES = {"pdf", "epub", "docx"}

class ProgressUpdate(BaseModel):
    progress: float # 0.0 - 1.0

@router.get("/")
async def get_documentos(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    documents = await get_documents_by_user(db, current_user.id)
    return [
        {
            "id": doc.id,
            "title": doc.title,
            "author": doc.author,
            "file_type": doc.file_type,
            "reading_progress": doc.reading_progress,
            "last_read_at": doc.last_read_at,
            "added_at": doc.added_at
        }
        for doc in documents
    ]

@router.get("/{document_id}")
async def get_documento(
    document_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    doc = await get_document_by_id(db, document_id, current_user.id)
    if not doc:
        raise HTTPException(status_code=404, detail="Documento no encontrado")
    return doc

@router.post("/nuevo")
async def nuevo_documento(
    title: str = Form(...),
    author: str = Form(None),
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    file_ext = file.filename.split(".")[-1].lower()
    if file_ext not in ALLOWED_TYPES:
        raise HTTPException(status_code=400, detail=f"Tipo no permitido. Usa: {ALLOWED_TYPES}")

    # guardar en disco
    user_storage = f"{STORAGE_PATH}/{current_user.id}"
    os.makedirs(user_storage, exist_ok=True)
    file_path = f"{user_storage}/{file.filename}"

    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    doc = await create_document(db, current_user.id, title, file_path, file_ext, author)
    return {"id": doc.id, "title": doc.title, "file_type": doc.file_type}

# reading progress
@router.patch("/{document_id}/progress")
async def update_progress(
    document_id: int,
    body: ProgressUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    doc = await get_document_by_id(db, document_id, current_user.id)
    if not doc:
        raise HTTPException(status_code=404, detail="Documento no encontrado")
    if not 0.0 <= body.progress <= 1.0:
        raise HTTPException(status_code=400, detail="Progreso debe estar entre 0.0 y 1.0")

    doc = await update_reading_progress(db, doc, body.progress)
    return {"id": doc.id, "reading_progress": doc.reading_progress}

@router.delete("/{document_id}")
async def delete_documento(
    document_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    doc = await get_document_by_id(db, document_id, current_user.id)
    if not doc:
        raise HTTPException(status_code=404, detail="Documento no encontrado")

    # eliminar de disco
    if os.path.exists(doc.file_path):
        os.remove(doc.file_path)

    await delete_document(db, doc)
    return {"ok": True}