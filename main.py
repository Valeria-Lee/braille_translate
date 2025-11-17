from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from utils.audio import speech_to_text
import requests
import pyaudio

app = FastAPI()

html = """
<!DOCTYPE html>
<html>
    <head>
        <title>Chat</title>
    </head>
    <body>
        <h1>WebSocket Chat</h1>
        <ul id='messages'>
        </ul>
        <script>
            var ws = new WebSocket("ws://localhost:8000/commands");

            ws.onopen = function() {
                console.log("Connected!");
                ws.send("hello-from-client");
            };

            ws.onerror = function(e) {
                console.error("WebSocket error:", e);
            };

            ws.onclose = function() {
                console.log("Disconnected!");
            };

            ws.onmessage = function(event) {
                var messages = document.getElementById('messages')
                var message = document.createElement('li')
                var content = document.createTextNode(event.data)
                message.appendChild(content)
                messages.appendChild(message)
            };
        </script>
    </body>
</html>
"""

@app.get("/")
async def root():
    return HTMLResponse(html)

# websocket
@app.websocket("/commands")
async def receive_command(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            text = speech_to_text() # para no dejar de recibir algo, de otra manera como que muere la comunicacion
            if text: # pero corta la ejecucion
                await websocket.send_text(text)
            # Limpia el ruido de fondo y con un llm reconoce que quiere
    except WebSocketDisconnect: # al momento de "retornar" se desconecta
        print("se desconecto el cliente")
    
@app.post("/browse")
async def browse(prompt: str):
    # Con un modelito hacer consultas concretas a la web.
    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "gemma3:270m",
            "prompt": prompt,
            "stream": False
        }
    )
    return response.json()

def search(title: str) -> None:
    pass

def translate(sentence: str) -> list:
    # se podria hacer con un dict
    # signos de puntuacion, matematicas
    # Esta funcion es solo para enviar senal, hay que hacerlo de tal forma que solo vaya enviando de tantos caracteres

    alphabet = ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','ñ','r','s','t','u','v','w','x','y','z','á','é','í','ó','ú','ü']
    braille_alphabet = ['⠁','⠃','⠉','⠙','⠑','⠋','⠛','⠓','⠊','⠚','⠅','⠇','⠍','⠝','⠕','⠏','⠟','⠻','⠗','⠎','⠞','⠥','⠧','⠺','⠭','⠽','⠵','⠷','⠮','⠌','⠬','⠾','⠳']

    braille_sentence = []

    for i in range(len(sentence)):
        index = alphabet.index(sentence[i])
        char = braille_alphabet[index]
        braille_sentence.append(char)
        
    return braille_sentence

# print(translate("hola"))