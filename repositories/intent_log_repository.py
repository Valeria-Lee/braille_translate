from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database.models.intent_log import IntentLog

async def get_intent_logs_by_user(db: AsyncSession, user_id: int) -> list[IntentLog]:
    result = await db.execute(select(IntentLog).where(IntentLog.user_id == user_id))
    return result.scalars().all()

async def create_intent_log(
    db: AsyncSession,
    user_id: int,
    query: str,
    intent: str,
    confidence: float
) -> IntentLog:
    log = IntentLog(
        user_id=user_id,
        query=query,
        intent=intent,
        confidence=confidence
    )
    db.add(log)
    await db.commit()
    await db.refresh(log)
    return log