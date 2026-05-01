from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database.models.braille_log import BrailleLog

async def get_braille_logs_by_user(db: AsyncSession, user_id: int) -> list[BrailleLog]:
    result = await db.execute(select(BrailleLog).where(BrailleLog.user_id == user_id))
    return result.scalars().all()

async def create_braille_log(
    db: AsyncSession,
    user_id: int,
    text: str,
    total_lines: int,
    document_id: int | None = None
) -> BrailleLog:
    log = BrailleLog(
        user_id=user_id,
        text=text,
        total_lines=total_lines,
        document_id=document_id
    )
    db.add(log)
    await db.commit()
    await db.refresh(log)
    return log