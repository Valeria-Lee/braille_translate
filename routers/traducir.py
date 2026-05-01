from fastapi import APIRouter, HTTPException
from utils.braille_translation import braille_translate
from device import braille_device

router = APIRouter(prefix="/traducir", tags=["traducir"])

@router.post("/")
async def traducir(text: str):
    if not text.strip():
        raise HTTPException(status_code=400, detail="El texto no puede estar vacío")

    if not braille_device.is_connected:
        raise HTTPException(status_code=503, detail="Dispositivo Braille no conectado")

    braille_data = braille_translate(text)
    success = await braille_device.load_text(braille_data)

    if not success:
        raise HTTPException(status_code=500, detail="Error enviando al dispositivo")

    return {
        "status": "ok",
        "total_lines": braille_device.total_lines,
        "cells": braille_device.cells
    }