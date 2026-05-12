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
import fitz
from docx import Document as DocxDocument
import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup
from utils.braille_translation import braille_translate, send_braille_characters
from utils.device import braille_device

router = APIRouter(prefix="/documentos", tags=["documentos"])

STORAGE_PATH = os.getenv("STORAGE_PATH")
ALLOWED_TYPES = {"pdf", "epub", "docx"}
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB

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

    contents = await file.read()
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="Archivo muy grande, máximo 50MB")
    
    # guardar en disco
    user_storage = f"{STORAGE_PATH}/{current_user.id}"
    os.makedirs(user_storage, exist_ok=True)
    file_path = f"{user_storage}/{file.filename}"

    with open(file_path, "wb") as f:
        f.write(contents)

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

    if os.path.exists(doc.file_path):
        os.remove(doc.file_path)

    await delete_document(db, doc)
    return {"ok": True}

class PublishRequest(BaseModel):
    is_public: bool
    category: str | None = None

@router.patch("/{document_id}/publish")
async def publish_documento(
    document_id: int,
    req: PublishRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    doc = await get_document_by_id(db, document_id, current_user.id)
    if not doc:
        raise HTTPException(status_code=404, detail="Documento no encontrado")

    doc.is_public = req.is_public
    doc.category = req.category
    await db.commit()
    await db.refresh(doc)

    return {"ok": True, "is_public": doc.is_public, "category": doc.category}

def extract_text(file_path: str, file_type: str) -> str:
    match file_type:
        case "pdf":
            doc = fitz.open(file_path)
            return " ".join(page.get_text() for page in doc)
        case "docx":
            doc = DocxDocument(file_path)
            return " ".join(p.text for p in doc.paragraphs if p.text.strip())
        case "epub":
            book = epub.read_epub(file_path)
            text = []
            for item in book.get_items_of_type(ebooklib.ITEM_DOCUMENT):
                soup = BeautifulSoup(item.get_content(), 'html.parser')
                text.append(soup.get_text())
            return " ".join(text)
        case _:
            return ""

@router.post("/{document_id}/read")
async def read_documento(
    document_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    doc = await get_document_by_id(db, document_id, current_user.id)
    if not doc:
        raise HTTPException(status_code=404, detail="Documento no encontrado")

    if not braille_device.is_connected:
        raise HTTPException(status_code=503, detail="Dispositivo no conectado")

    text = extract_text(doc.file_path, doc.file_type)

    text = " ".join(text.split())  # collapse whitespace
    text = text.strip()

    if not text.strip():
        raise HTTPException(status_code=400, detail="No se pudo extraer texto del documento")

    braille_data = braille_translate(text)
    # dots = send_braille_characters(braille_data)
    ok = await braille_device.load_text(braille_data)

    await update_reading_progress(db, doc, 0.0)

    return {
        "ok": ok,
        "total_lines": braille_device.total_lines,
        "current_line": braille_device.current_line,
        "title": doc.title
    }