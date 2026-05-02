from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from database.models.document import Document
from datetime import datetime

async def get_documents_by_user(db: AsyncSession, user_id: int) -> list[Document]:
    result = await db.execute(select(Document).where(Document.user_id == user_id))
    return result.scalars().all()

async def get_document_by_id(db: AsyncSession, document_id: int, user_id: int) -> Document | None:
    result = await db.execute(
        select(Document).where(Document.id == document_id, Document.user_id == user_id)
    )
    return result.scalar_one_or_none()

async def create_document(
    db: AsyncSession,
    user_id: int,
    title: str,
    file_path: str,
    file_type: str,
    author: str | None = None
) -> Document:
    document = Document(
        user_id=user_id,
        title=title,
        file_path=file_path,
        file_type=file_type,
        author=author
    )
    db.add(document)
    await db.commit()
    await db.refresh(document)
    return document

async def update_reading_progress(
    db: AsyncSession,
    document: Document,
    progress: float
) -> Document:
    document.reading_progress = progress
    document.last_read_at = datetime.now()
    await db.commit()
    await db.refresh(document)
    return document

async def delete_document(db: AsyncSession, document: Document) -> None:
    await db.delete(document)
    await db.commit()