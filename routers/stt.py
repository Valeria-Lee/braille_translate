from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from starlette.concurrency import run_in_threadpool
from utils.audio import new_recognizer, transcribe_chunk

router = APIRouter(tags=["stt"])

@router.websocket("/transcribe")
async def transcribe_ws(websocket: WebSocket):
    await websocket.accept()
    recognizer = new_recognizer()
    try:
        while True:
            chunk = await websocket.receive_bytes()
            result = await run_in_threadpool(transcribe_chunk, chunk, recognizer)
            await websocket.send_json(result)

            if result["type"] == "transcription" and result["text"]:
                await websocket.close()
                return
    except WebSocketDisconnect:
        pass