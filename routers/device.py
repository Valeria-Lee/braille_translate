from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from database.connection import get_db
from database.models.user import User
from auth.dependencies import get_current_user
from repositories.device_repository import get_device_by_user, create_device, get_device_by_token
from utils.device import braille_device
import secrets
from datetime import datetime, timedelta

router = APIRouter(prefix="/device", tags=["device"])
pending_pairs: dict = {}

class DeviceRegisterRequest(BaseModel):
    device_token: str
    cells: int = 1

class PairConfirmRequest(BaseModel):
    device_id: str
    cells: int = 1

@router.get("/status")
async def device_status(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    device = await get_device_by_user(db, current_user.id)
    cells = braille_device.cells if braille_device.is_connected else (device.cells if device else 0)
    
    return {
        "connected":    braille_device.is_connected,
        "cells":        cells,
        "current_line": braille_device.current_line,
        "total_lines":  braille_device.total_lines,
    }

@router.post("/off")
async def device_off(
    current_user: User = Depends(get_current_user)
):
    ok = await braille_device.emergency_off()
    return {"ok": ok}

@router.post("/next")
async def next_line(
    current_user: User = Depends(get_current_user)
):
    ok = await braille_device.next_line()
    return {
        "ok":           ok,
        "current_line": braille_device.current_line,
        "total_lines":  braille_device.total_lines,
    }

@router.post("/prev")
async def prev_line(
    current_user: User = Depends(get_current_user)
):
    ok = await braille_device.prev_line()
    return {
        "ok":           ok,
        "current_line": braille_device.current_line,
        "total_lines":  braille_device.total_lines,
    }

@router.websocket("/ws")
async def device_endpoint(websocket: WebSocket):
    await websocket.accept(
        {
            "type": "config",
            "pausa_chars": 500
        }
    )
    try:
        hello = await asyncio.wait_for(websocket.receive_json(), timeout=30.0)
        if hello.get("type") != "hello":
            await websocket.close()
            return
        cells = hello.get("cells", 1)
        await braille_device.on_connect(websocket, cells)
        while True:
            msg = await websocket.receive_json()
            logger.info(f"ESP mensaje: {msg}")
            if msg.get("type") == "ping":
                continue
            await braille_device.on_message(msg)
    except WebSocketDisconnect:
        logger.warning("ESP desconectado por WebSocketDisconnect")
        await braille_device.on_disconnect()
    except Exception as e:
        logger.error(f"Error en /device: {e}")
        await braille_device.on_disconnect()

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

@router.patch("/cells")
async def update_cells(
    cells: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    device = await get_device_by_user(db, current_user.id)
    if not device:
        raise HTTPException(status_code=404, detail="No tienes un dispositivo registrado")
    
    device.cells = cells
    await db.commit()
    await db.refresh(device)

    braille_device._cells = cells

    return {"ok": True, "cells": device.cells}

@router.patch("/config")
async def update_config(
    pausa_chars: int,
    current_user: User = Depends(get_current_user)
):
    braille_device._pausa_chars = pausa_chars
    if braille_device.is_connected:
        await braille_device._ws.send_json({
            "type": "config",
            "pausa_chars": pausa_chars
        })
    return {"ok": True, "pausa_chars": pausa_chars}