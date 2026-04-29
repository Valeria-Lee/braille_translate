from vosk import Model, KaldiRecognizer, SetLogLevel
import json, os
from dotenv import load_dotenv

load_dotenv()
SetLogLevel(0)

_model = None

def get_model():
    global _model
    if _model is None:
        _model = Model(os.getenv("MODEL_PATH"))
    return _model

def transcribe_chunk(data: bytes, recognizer: KaldiRecognizer) -> dict:
    if recognizer.AcceptWaveform(data):
        result = json.loads(recognizer.Result())
        return {"type": "transcription", "text": result.get("text", "")}
    else:
        partial = json.loads(recognizer.PartialResult())
        return {"type": "partial", "text": partial.get("partial", "")}

def new_recognizer() -> KaldiRecognizer:
    return KaldiRecognizer(get_model(), 16000)