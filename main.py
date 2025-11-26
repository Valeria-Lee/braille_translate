from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from utils.audio import speech_to_text
from utils.braille_translation import braille_translate, send_braille_characters
from starlette import status
from starlette.responses import RedirectResponse
from starlette.concurrency import run_in_threadpool
from rasa.core.agent import Agent
from contextlib import asynccontextmanager
from dotenv import load_dotenv
import requests, uvicorn, os, re

load_dotenv()

MODELO_ENTRENADO = model_path = os.getenv("NLU_MODEL_PATH")
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
                    li.textContent = "🎤 Texto: " + data.text +
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


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    global agent
    agent = Agent.load(MODELO_ENTRENADO)
    yield

app = FastAPI(lifespan=lifespan)
    
@app.get("/")
async def root():
    return HTMLResponse(html)

# websocket
@app.websocket("/commands")
async def receive_command(websocket: WebSocket):
    if agent:
        await websocket.accept()
        try:
            while True:
                final_text = await run_in_threadpool(speech_to_text)

                if not final_text:
                    continue

                print("Final:", final_text)

                # clasificar intencion con rasa
                nav_task = await agent.parse_message(final_text)
                prediction_intent = nav_task["intent"]
                intent = prediction_intent["name"]
                confidence = prediction_intent["confidence"]

                # enviar mensaje final al frontend
                await websocket.send_json({
                    "type": "transcription",
                    "text": final_text,
                    "intent": intent,
                    "confidence": confidence
                })
                    
                if intent == "busqueda_web":
                    result = await browse(final_text)
                    await websocket.send_json({
                    "type": "browse",
                        "data": result
                    })   
                 
                elif intent == "acceso_directo":
                    result = search(final_text)
                    await websocket.send_json({
                        "type": "search",
                        "data": result
                    })

                else:
                    await websocket.send_json({
                        "type": "unknown",
                        "intent": intent,
                        "message": "Intent no implementado"
                    })
                        
        except WebSocketDisconnect:
            print("Cliente desconectado")
    else:
        print("no hay modelito cargado")
    
'''
elif intent == "upload":
await websocket.send_json({
    "type": "upload",
    "status": "ready"
})
'''

@app.post("/browse")
async def browse(prompt: str):
    system_prompt = (
        "Eres un asistente de búsqueda. Tu tarea es proporcionar una respuesta "
        "útil y completa que responda directamente a la pregunta del usuario. "
        "La respuesta debe ser concisa, en no más de 50 palabras. "
        "No uses introducciones, negritas, cursivas ni saltos de línea. "
        "Da una respuesta directa y clara."
    )
    
    full_prompt = f"{system_prompt}\n\nUsuario: {prompt}"

    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "gemma3:270m",
            "prompt": full_prompt, 
            "stream": False,
            "options": {
                "temperature": 0.1,  # menos creativo
                "num_ctx": 1024 # longitud max del resumen
            }
        }
    )
    full_response = response.json()
    formatted_text_response = full_response["response"]

    text_response = re.sub(r'(\*\*|\*|__|_|`)', '', formatted_text_response)
    text_response = re.sub(r'\n', ' ', text_response)

    return {"Respuesta": text_response}

@app.post("/upload")
async def upload(document) -> None:
    pass

@app.post("/search")
async def search(title: str) -> None:
    pass # va a hacer una tonteriita que busque por palabras clave.