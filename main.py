from fastapi import FastAPI, WebSocket, WebSocketDisconnect, APIRouter
from fastapi.responses import HTMLResponse
from utils.audio import speech_to_text
from utils.braille_translation import braille_translate, send_braille_characters
from utils.classification.task_classification import classify
from starlette.concurrency import run_in_threadpool
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from routers import users, documentos, traducir, test_braille
import uvicorn

load_dotenv()

app = FastAPI()

app.include_router(users.router)
app.include_router(documentos.router)
app.include_router(traducir.router)
app.include_router(test_braille.router)

silence_seconds = 0

html = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Chat</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 50px auto;
            padding: 20px;
        }
        #messages {
            list-style-type: none;
            padding: 0;
            max-height: 500px;
            overflow-y: auto;
        }
        #messages li {
            padding: 10px;
            margin: 5px 0;
            border-radius: 5px;
            background-color: #f0f0f0;
        }
        .transcription {
            background-color: #e3f2fd;
            font-weight: bold;
        }
        .data {
            background-color: #e8f5e9;
            font-family: monospace;
            white-space: pre-wrap;
        }
        .error {
            background-color: #ffebee;
            color: #c62828;
        }
    </style>
</head>
<body>
    <h1>WebSocket Chat - Traductor Braille</h1>
    <h3>Status: <span id="status">Conectando...</span></h3>
    <ul id="messages"></ul>

    <script>
        const ws = new WebSocket("ws://localhost:8000/commands");

        ws.onopen = function() {
            console.log("Connected!");
            document.getElementById("status").textContent = "Conectado ✓";
            document.getElementById("status").style.color = "green";
        };

        ws.onerror = function() {
            document.getElementById("status").textContent = "Error ✗";
            document.getElementById("status").style.color = "red";
        };

        ws.onclose = function() {
            console.log("Disconnected!");
            document.getElementById("status").textContent = "Desconectado";
            document.getElementById("status").style.color = "orange";
        };

        ws.onmessage = function(event) {
            const messages = document.getElementById("messages");
            const li = document.createElement("li");

            try {
                const data = JSON.parse(event.data);

                if (data.type === "transcription") {
                    li.className = "transcription";
                    li.textContent = "Texto: " + data.text +
                                     " | Intent: " + data.intent +
                                     " | Confianza: " + (data.confidence * 100).toFixed(2) + "%";
                }
                else if (data.type === "partial_transcription") {
                    li.className = "transcription";
                    li.textContent = "⏳ Parcial: " + data.text;
                }
                else {
                    li.textContent = event.data;
                }

            } catch (e) {
                li.textContent = event.data;
            }

            messages.appendChild(li);
            messages.scrollTop = messages.scrollHeight;
        };
    </script>
</body>
</html>
"""

async def handle_intent(intent: str, text: str, websocket: WebSocket):
    if intent == "traducir":
        braille = braille_translate(text)
        await run_in_threadpool(send_braille_characters, braille)
        await websocket.send_json({
            "type": "traduccion",
            "braille": braille
        })
    elif intent == "agregar_documento":
        await websocket.send_json({
            "type": "redirect",
            "url": "/documentos/nuevo"
        })
    elif intent == "acceder_documento":
        await websocket.send_json({
            "type": "redirect",
            "url": "/documentos"
        })
    elif intent == "buscar_catalogo":
        await websocket.send_json({
            "type": "redirect",
            "url": "/catalogo"
        })

@app.get("/")
async def root():
    return HTMLResponse(html)

# websocket
@app.websocket("/commands")
async def receive_command(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            final_text = await run_in_threadpool(speech_to_text)

            if not final_text:
                continue

            nav_task = classify(final_text)

            if nav_task["intent"] == "fallback":
                await websocket.send_json({
                    "type": "fallback",
                    "message": "No entendí, ¿puedes repetirlo?"
                })
            elif nav_task["intent"] == "clarification":
                await websocket.send_json({
                    "type": "clarification",
                    "message": f"¿Quisiste decir {nav_task['candidate']}?",
                    "candidate": nav_task["candidate"]
                })
            else:
                await handle_intent(nav_task["intent"], final_text, websocket)

    except WebSocketDisconnect:
        print("Cliente desconectado")