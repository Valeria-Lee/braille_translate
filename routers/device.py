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


@app.get("/status")
async def device_status():
    return {
        "connected":    braille_device.is_connected,
        "cells":        braille_device.cells,
        "current_line": braille_device.current_line,
        "total_lines":  braille_device.total_lines,
    }

@app.post("/off")
async def device_off():
    ok = await braille_device.emergency_off()
    return {"ok": ok}

@app.post("/next")
async def next_line():
    ok = await braille_device.next_line()
    return {
        "ok":           ok,
        "current_line": braille_device.current_line,
        "total_lines":  braille_device.total_lines,
    }

@app.post("/prev")
async def prev_line():
    ok = await braille_device.prev_line()
    return {
        "ok":           ok,
        "current_line": braille_device.current_line,
        "total_lines":  braille_device.total_lines,
    }

@app.websocket("/device")
async def device_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        hello = await asyncio.wait_for(websocket.receive_json(), timeout=30.0)
        if hello.get("type") != "hello":
            await websocket.close()
            return
        cells = hello.get("cells", 1)
        await braille_device.on_connect(websocket, cells)
        while True:
            msg = await websocket.receive_json()
            logger.info(f"ESP mensaje: {msg}")  # ← agregar
            if msg.get("type") == "ping":
                continue
            await braille_device.on_message(msg)
    except WebSocketDisconnect:
        logger.warning("ESP desconectado por WebSocketDisconnect")
        await braille_device.on_disconnect()
    except Exception as e:
        logger.error(f"Error en /device: {e}")
        await braille_device.on_disconnect()

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

@router.post("/pair/request")
async def pair_request(device_id: str):
    code = secrets.token_hex(3).upper()
    pending_pairs[device_id] = {
        "code": code,
        "expires": datetime.now() + timedelta(minutes=5)
    }
    # no auth needed — ESP8266 calls this
    return {"ok": True, "expires_in": 300}

@router.post("/pair/confirm")
async def pair_confirm(
    req: PairConfirmRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    pair = pending_pairs.get(req.device_id)

    if not pair:
        raise HTTPException(status_code=404, detail="No hay dispositivo esperando")

    if datetime.now() > pair["expires"]:
        del pending_pairs[req.device_id]
        raise HTTPException(status_code=408, detail="Expirado, presiona el botón de nuevo")

    existing = await get_device_by_user(db, current_user.id)
    if existing:
        raise HTTPException(status_code=400, detail="Ya tienes un dispositivo registrado")

    device = await create_device(db, current_user.id, req.device_id)
    del pending_pairs[req.device_id]

    return {"ok": True, "device_id": req.device_id, "cells": device.cells}