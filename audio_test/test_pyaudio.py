import wave

import pyaudio

CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1 # mono
RATE = 44100
RECORD_SECONDS = 5
OUTPUT_FILE = "output.wav"

with wave.open(OUTPUT_FILE, 'wb') as wf:
    p = pyaudio.PyAudio()
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)

    # con esto ya "escucha" el audio
    stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True)

    print('Recording...')
    while True: # o guardar multiples chunks e irlos procesando
        # record for chunks
        for _ in range(0, RATE // CHUNK * RECORD_SECONDS):
            wf.writeframes(stream.read(CHUNK))
    print('Done')

    stream.close()
    p.terminate()
