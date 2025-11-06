from fastapi import FastAPI
import requests

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}

def receive_command(command: str) -> None:
    # Limpia el ruido de fondo y con un llm reconoce que quiere
    pass

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