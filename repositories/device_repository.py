from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database.models.device import Device
from datetime import datetime

async def get_device_by_user(db: AsyncSession, user_id: int) -> Device | None:
    result = await db.execute(select(Device).where(Device.user_id == user_id))
    return result.scalar_one_or_none()

async def get_device_by_token(db: AsyncSession, token: str) -> Device | None:
    result = await db.execute(select(Device).where(Device.device_token == token))
    return result.scalar_one_or_none()

async def create_device(db: AsyncSession, user_id: int, token: str, cells: int = 1) -> Device:
    device = Device(user_id=user_id, device_token=token, cells=cells)
    db.add(device)
    await db.commit()
    await db.refresh(device)
    return device

async def update_device_last_connected(db: AsyncSession, device: Device) -> Device:
    device.last_connected = datetime.now()
    await db.commit()
    await db.refresh(device)
    return device