from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from database.connection import get_db
from database.models.user import User
from auth.dependencies import get_current_user
from repositories.device_repository import get_device_by_user, create_device, get_device_by_token
import secrets
from datetime import datetime, timedelta

router = APIRouter(prefix="/device", tags=["device"])

class DeviceRegisterRequest(BaseModel):
    device_token: str
    cells: int = 1

@router.post("/register")
async def register_device(
    req: DeviceRegisterRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # check user doesn't already have a device
    existing = await get_device_by_user(db, current_user.id)
    if existing:
        raise HTTPException(status_code=400, detail="Ya tienes un dispositivo registrado")

    # check token isn't taken by another user
    token_taken = await get_device_by_token(db, req.device_token)
    if token_taken:
        raise HTTPException(status_code=400, detail="Token ya registrado")

    device = await create_device(db, current_user.id, req.device_token, req.cells)
    return {"id": device.id, "device_token": device.device_token, "cells": device.cells}