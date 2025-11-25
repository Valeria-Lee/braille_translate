from vosk import Model, KaldiRecognizer, SetLogLevel
from dotenv import load_dotenv
import pyaudio
import os
import json
import time
# libreria de sonido: pyaudio, libreria de speechrecognition: vosk
# depende del procesador la capacidad de vosk

def speech_to_text():
    load_dotenv() # cambiar a settings + pydantic
    model_path = os.getenv("MODEL_PATH")

    SetLogLevel(0) # semilimpia el audio

    RATE = 16000 # herz, standard

    CHUNK = 4000
    FORMAT = pyaudio.paInt16
    CHANNELS = 1 # mono

    SILENCE_TIMEOUT = 10

    p = pyaudio.PyAudio()

    try:
        model = Model(model_path) # absolute path
    except Exception as e:
        print("es necesario descargar el modelo y nombrarlo como model, cambiar el path por el path absoluto en su sistema")
        exit()

    recognizer = KaldiRecognizer(model, RATE)

    # con esto ya "escucha" el audio
    stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True)

    print('Recording...')

    last_partial = ""
    last_speech_time = time.time()

    while True:
        data = stream.read(CHUNK, exception_on_overflow=False)
            
        if not data:
            break # cuando se queda en silencio, se espera a que acabe el chunk.

        if recognizer.AcceptWaveform(data):
            text_result = json.loads(recognizer.Result())["text"]
            print(f"El texto resultante: {text_result}")
            return text_result

        partial_json = json.loads(recognizer.PartialResult())
        partial = partial_json.get("partial", "")

        if partial:
            print("partial:", partial)
            last_partial = partial
            last_speech_time = time.time()
        else:
            # si el tiempo actual y el de la ultima vez que se hablo es mayor a 7 segundos.
            if time.time() - last_speech_time > SILENCE_TIMEOUT:
                print("partial res:", last_partial)
                return last_partial

    stream.stop_stream()
    stream.close()
    p.terminate()