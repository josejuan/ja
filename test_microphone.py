import pyaudio
import queue

CHUNK_SECONDS = 1  # Duración de cada chunk en segundos
SAMPLE_RATE = 16000  # Tasa de muestreo en Hz
CHUNK_SIZE = SAMPLE_RATE * CHUNK_SECONDS  # Tamaño de cada chunk de audio en bytes

def audio_capture_thread(audio_queue):
    p = pyaudio.PyAudio()
    stream = p.open(
        format=pyaudio.paInt16,
        channels=1,
        rate=SAMPLE_RATE,
        input=True,
        frames_per_buffer=CHUNK_SIZE
    )

    try:
        while True:
            audio_chunk = stream.read(CHUNK_SIZE)
            audio_queue.put(audio_chunk)
    except KeyboardInterrupt:
        print("Audio capture stopped.")
    finally:
        stream.stop_stream()
        stream.close()
        p.terminate()

if __name__ == "__main__":
    audio_queue = queue.Queue()
    audio_capture_thread(audio_queue)

