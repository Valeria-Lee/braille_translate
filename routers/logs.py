from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from database.connection import get_db
from database.models.user import User
from auth.dependencies import get_current_user
from repositories.braille_log_repository import get_braille_logs_by_user, create_braille_log
from device import braille_device
from utils.braille_translation import braille_translate, send_braille_characters

router = APIRouter(prefix="/logs", tags=["logs"])

# mensajes de braille
@router.get("/braille")
async def get_braille_logs(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    logs = await get_braille_logs_by_user(db, current_user.id)
    return [
        {
            "id": log.id,
            "text": log.text,
            "total_lines": log.total_lines,
            "document_id": log.document_id,
            "created_at": log.created_at
        }
        for log in logs
    ]

# resend a past log to device
@router.post("/braille/{log_id}/send")
async def resend_braille_log(
    log_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    logs = await get_braille_logs_by_user(db, current_user.id)
    log = next((l for l in logs if l.id == log_id), None)

    if not log:
        raise HTTPException(status_code=404, detail="Log no encontrado")

    if not braille_device.is_connected:
        raise HTTPException(status_code=503, detail="Dispositivo no conectado")

    braille_data = braille_translate(log.text)
    dots = send_braille_characters(braille_data)
    await braille_device.load_text(dots)

    return {
        "ok": True,
        "total_lines": braille_device.total_lines,
        "current_line": braille_device.current_line
    }