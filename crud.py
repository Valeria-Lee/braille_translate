 # Operaciones de Create, Read, Update y Delete para la base de datos
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

import models, schemas

async def create_user(db: AsyncSession, user: schemas.UserCreate):
    db_user = models.User(email=user.email, name=user.name)
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user

async def get_user(db: AsyncSession, user_id: int):
    result = await db.execute(select(models.User).where(models.User.id == user_id))
    return result.scalar_one_or_none()

async def get_users(db: AsyncSession):
    result = await db.execute(select(models.User))
    return result.scalars().all()

async def delete_user(db: AsyncSession, user_id: int):
    user = await get_user(db, user_id)
    if not user:
        return None
    await db.delete(user)
    await db.commit()
    return True

async def create_file(db: AsyncSession, file: schemas.FileCreate, user_id: int):
    db_file = models.File(
        title=file.title,
        file=file.file,
        user_id=user_id
    )
    db.add(db_file)
    await db.commit()
    await db.refresh(db_file)
    return db_file

async def get_file(db: AsyncSession, file_id: int):
    result = await db.execute(select(models.File).where(models.File.id == file_id))
    return result.scalar_one_or_none()

async def get_files_by_user(db: AsyncSession, user_id: int):
    result = await db.execute(select(models.File).where(models.File.user_id == user_id))
    return result.scalars().all()

async def delete_file(db: AsyncSession, file_id: int):
    file = await get_file(db, file_id)
    if not file:
        return None
    await db.delete(file)
    await db.commit()
    return True
