import pyaudio
from scipy.io import wavfile
import noisereduction as nr
from vosk import Model, KaldiRecognizer, SetLogLevel

def speech_to_text():
    load_dotenv() # settings + pydantic cuando se haga deploy
    model_path = os.getenv("MODEL_PATH")

    SetLogLevel(0)

    RATE = 16000 # herz, standard
    CHUNK = 4000
    FORMAT = pyaudio.paInt16
    CHANNELS = 1 # mono

    p = pyaudio.PyAudio()

    stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True)

    recognizer = KaldiRecognizer(model, RATE)

    while True:
        data = stream.read(CHUNK, exception_on_overflow=False) # bytes
        reduced_noise_data = nr.reduce_noise(y=data, sr=RATE) # still bytes
            
        if not reduced_noise_data: # change it to data if it's not correctly detecting it
            break

        if recognizer.AcceptWaveform(reduced_noise_data):
            result = recognizer.Result()

        partial_result = recognizer.PartialResult()

    stream.stop_stream()
    stream.close()
    p.terminate()