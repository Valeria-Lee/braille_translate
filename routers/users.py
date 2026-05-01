from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from database.connection import get_db
from repositories.user_repository import get_user_by_email, create_user
from auth.hashing import hash_password, verify_password
from auth.jwt import create_access_token

router = APIRouter(prefix="/users", tags=["users"])

class RegisterRequest(BaseModel):
    email: str
    password: str

@router.post("/register")
async def register(req: RegisterRequest, db: AsyncSession = Depends(get_db)):
    existing = await get_user_by_email(db, req.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email ya registrado")
    
    user = await create_user(db, req.email, hash_password(req.password))
    return {"id": user.id, "email": user.email}

@router.post("/login")
async def login(form: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    user = await get_user_by_email(db, form.username)
    if not user or not verify_password(form.password, user.password):
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")
    
    token = create_access_token(user.id)
    return {"access_token": token, "token_type": "bearer"}