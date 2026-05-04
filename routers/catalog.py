from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database.connection import get_db
from database.models.document import Document
from slowapi import Limiter
from slowapi.util import get_remote_address
from fastapi import Request

router = APIRouter(prefix="/catalogo", tags=["catalogo"])
limiter = Limiter(key_func=get_remote_address)

@router.get("/")
@limiter.limit("30/minute")
async def get_catalogo(
    request: Request,
    category: str | None = Query(None),
    db: AsyncSession = Depends(get_db)
):
    query = select(Document).where(Document.is_public == True)
    if category:
        query = query.where(Document.category == category)
    
    result = await db.execute(query)
    documents = result.scalars().all()

    return [
        {
            "id": doc.id,
            "title": doc.title,
            "author": doc.author,
            "file_type": doc.file_type,
            "category": doc.category,
            "added_at": doc.added_at
        }
        for doc in documents
    ]

@router.get("/categories")
@limiter.limit("30/minute")
async def get_categories(
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Document.category)
        .where(Document.is_public == True)
        .where(Document.category != None)
        .distinct()
    )
    categories = [row[0] for row in result.fetchall()]
    return {"categories": categories}