from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from utils.audio import new_recognizer, transcribe_chunk
from utils.braille_translation import braille_translate
from utils.classification.semantic_classifier import classify
from utils.device import braille_device
from starlette.concurrency import run_in_threadpool
from dotenv import load_dotenv
from routers import traducir, test_braille, users, documentos, device
import asyncio
import logging

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

#TODO: definir rutas, pruebas locales.

app = FastAPI()
app.include_router(traducir.router)
app.include_router(test_braille.router)
app.include_router(users.router)

class TextoRequest(BaseModel):
    text: str
    char_qty: int = 1 

@app.get("/")
async def root():
    return {"status": "BrailLearn API running"}

@app.get("/device/status")
async def device_status():
    return {
        "connected":    braille_device.is_connected,
        "cells":        braille_device.cells,
        "current_line": braille_device.current_line,
        "total_lines":  braille_device.total_lines,
    }

@app.post("/device/off")
async def device_off():
    ok = await braille_device.emergency_off()
    return {"ok": ok}


@app.post("/traducir")
async def traducir_texto(req: TextoRequest):
    if not req.text.strip():
        return {"error": "Texto vacío"}

    braille_data = braille_translate(req.text)

    ok = await braille_device.load_text(braille_data)

    return {
        "ok":           ok,
        "total_lines":  braille_device.total_lines,
        "current_line": braille_device.current_line,
        "connected":    braille_device.is_connected,
    }


@app.post("/device/next")
async def next_line():
    ok = await braille_device.next_line()
    return {
        "ok":           ok,
        "current_line": braille_device.current_line,
        "total_lines":  braille_device.total_lines,
    }


@app.post("/device/prev")
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
        hello = await asyncio.wait_for(websocket.receive_json(), timeout=10.0)

        if hello.get("type") != "hello":
            logger.error(f"Esperaba hello, recibí: {hello}")
            await websocket.close()
            return

        cells = hello.get("cells", 1)
        await braille_device.on_connect(websocket, cells)

        while True:
            msg = await websocket.receive_json()
            if msg.get("type") == "ping":
                continue
            await braille_device.on_message(msg)

    except WebSocketDisconnect:
        await braille_device.on_disconnect()
    except Exception as e:
        logger.error(f"Error en /device: {e}")
        await braille_device.on_disconnect()


async def handle_intent(intent: str, text: str, websocket: WebSocket):
    if intent == "traducir":
        braille_data = braille_translate(text)
        ok = await braille_device.load_text(braille_data)
        await websocket.send_json({
            "type":         "traduccion",
            "text":         text,
            "device_ok":    ok,
            "total_lines":  braille_device.total_lines,
            "connected":    braille_device.is_connected,
        })
    elif intent == "agregar_documento":
        await websocket.send_json({"type": "redirect", "url": "/documentos/nuevo"})
    elif intent == "acceder_documento":
        await websocket.send_json({"type": "redirect", "url": "/documentos"})
    elif intent == "buscar_catalogo":
        await websocket.send_json({"type": "redirect", "url": "/catalogo"})


@app.websocket("/commands")
async def commands_endpoint(websocket: WebSocket):
    await websocket.accept()
    recognizer = new_recognizer()
    try:
        while True:
            data = await websocket.receive_bytes()
            result = transcribe_chunk(data, recognizer)

            if result["type"] == "partial":
                await websocket.send_json({
                    "type": "partial_transcription",
                    "text": result["text"]
                })
            elif result["type"] == "transcription" and result["text"]:
                final_text = result["text"]
                nav_task = classify(final_text)

                if nav_task["intent"] == "fallback":
                    await websocket.send_json({
                        "type":    "fallback",
                        "message": "No entendí, ¿puedes repetirlo?"
                    })
                elif nav_task["intent"] == "clarification":
                    await websocket.send_json({
                        "type":      "clarification",
                        "message":   f"¿Quisiste decir {nav_task['candidate']}?",
                        "candidate": nav_task["candidate"]
                    })
                else:
                    await handle_intent(nav_task["intent"], final_text, websocket)

    except WebSocketDisconnect:
        logger.info("Cliente /commands desconectado")