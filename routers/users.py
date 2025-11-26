from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from models import User
from schemas import UserCreate, UserResponse
from database import get_session

router = APIRouter(prefix="/users", tags=["Users"])

@router.post("/", response_model=UserResponse)
async def create_user(user: UserCreate, db: AsyncSession = Depends(get_session)):
    new_user = User(email=user.email, name=user.name)
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: int, db: AsyncSession = Depends(get_session)):
    return await db.get(User, user_id)
