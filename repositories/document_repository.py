from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database.models.document import Document

async def get_documents_by_user(db: AsyncSession, user_id: int) -> list[Document]:
    result = await db.execute(select(Document).where(Document.user_id == user_id))
    return result.scalars().all()

async def get_document_by_id(db: AsyncSession, document_id: int, user_id: int) -> Document | None:
    result = await db.execute(
        select(Document).where(Document.id == document_id, Document.user_id == user_id)
    )
    return result.scalar_one_or_none()

async def create_document(db: AsyncSession, user_id: int, title: str, content: str) -> Document:
    document = Document(user_id=user_id, title=title, content=content)
    db.add(document)
    await db.commit()
    await db.refresh(document)
    return document

async def delete_document(db: AsyncSession, document: Document) -> None:
    await db.delete(document)
    await db.commit()