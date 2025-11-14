import pyaudio
from vosk import Model, KaldiRecognizer, SetLogLevel
# libreria de sonido: pyaudio, libreria de speechrecognition: vosk
# depende del procesador la capacidad de vosk

# pasar a una variable env
model_path = '/home/valeria/Documents/infomat/traductor/audio_test/model'

SetLogLevel(0) # semilimpia el audio

SAMPLE_RATE = 16000 # herz, standard

CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1 # mono
# RATE = 44100
RECORD_SECONDS = 5

def speechToText():
    p = pyaudio.PyAudio()

    try:
        model = Model(model_path) # absolute path
    except Exception as e:
        print("es necesario descargar el modelo y nombrarlo como model, cambiar el path por el path absoluto en su sistema")
        exit()

    recognizer = KaldiRecognizer(model, SAMPLE_RATE)

    # con esto ya "escucha" el audio
    stream = p.open(format=FORMAT, channels=CHANNELS, rate=SAMPLE_RATE, input=True)

    print('Recording...')

    while True:
        data = stream.read(CHUNK, exception_on_overflow=False)

        if not data:
            break

        if recognizer.AcceptWaveform(data):
            text = recognizer.Result()
            print(text)

    stream.stop_stream()
    stream.close()
    p.terminate()