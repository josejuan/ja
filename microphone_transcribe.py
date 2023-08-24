import torch
import nemo
import nemo.collections.asr as asr
import pyaudio
import queue
import pprint
import numpy as np
import wave
import struct
from datetime import datetime
import http.server
import socketserver
import threading
import urllib.request as httpr

MODEL_NAME='stt_es_quartznet15x5'

HTTP_IP="0.0.0.0"
HTTP_PORT=9057
SERVER_URL='http://192.168.0.2:9057'

CHUNK_SECONDS = 1
SAMPLE_RATE = 16000
DEVICE_INDEX=11
PAUSE_CHUNKS=2
PAUSE_MAX_DB=75
DIALOG_MIN_CHUNKS=1
DIALOG_MAX_CHUNKS = 30
TEMP='/tmp/microphone_transcribe.py.temp.wav'

CHUNK_SIZE = SAMPLE_RATE * CHUNK_SECONDS

qn = asr.models.EncDecCTCModel.from_pretrained(model_name=MODEL_NAME)
p = pyaudio.PyAudio()
do_reset = False

# Use `arecord -D hw:2,0 --dump-hw-params` to get supported sample rates...
# Test using `aplay -r 16000 -f S32_LE microphone_transcribe.py.temp.wav`

class MqRequestHandler(http.server.BaseHTTPRequestHandler):
    def do_POST(self):
        global do_reset
        text = self.rfile.read(int(self.headers['Content-Length'])).decode('utf-8').strip()
        print(f"$$ recibido: {text}", flush=True)
        if text == "do reset":
            do_reset = True
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'Ok')

def mq_http_server():
    print(f"Starting web server on {HTTP_IP}:{HTTP_PORT}")
    with socketserver.TCPServer((HTTP_IP, HTTP_PORT), MqRequestHandler) as s:
        s.serve_forever()

def list_input_devices():
    device_count = p.get_device_count()
    print("Available input devices:")
    for i in range(device_count):
        device_info = p.get_device_info_by_index(i)
        if device_info['maxInputChannels'] > 0:
            print(f"Index {i}: {device_info['name']}")

def audio_capture_thread(buff):
    stream = p.open(format=pyaudio.paInt32, channels=1, rate=SAMPLE_RATE, input=True, frames_per_buffer=CHUNK_SIZE, input_device_index=DEVICE_INDEX)
    try:
        global do_reset
        while True:
            paused_chunks = 0
            dialog_chunks = 0
            while not do_reset and paused_chunks < PAUSE_CHUNKS:
                audio_chunk = stream.read(CHUNK_SIZE)

                d = np.frombuffer(audio_chunk, np.int32).astype(np.float)
                energy = 10 * np.log10(np.sqrt((d*d).sum()/len(d)))
                #print(f"Captured with {energy} db energy.", flush=True)

                buff.extend(audio_chunk)

                if energy <= PAUSE_MAX_DB:
                    paused_chunks = paused_chunks + 1
                else:
                    dialog_chunks = dialog_chunks + 1
                    if dialog_chunks > DIALOG_MAX_CHUNKS:
                        do_reset = True

            if not do_reset and dialog_chunks >= DIALOG_MIN_CHUNKS:
                t0 = datetime.now()
                stream.stop_stream()
                print("Procesando buffer...", flush=True)
                with wave.open(TEMP, "wb") as f:
                    f.setnchannels(1)
                    f.setsampwidth(p.get_sample_size(pyaudio.paInt32))
                    f.setframerate(SAMPLE_RATE)
                    f.writeframes(buff)
                t1 = datetime.now()
                for t in qn.transcribe(paths2audio_files=[TEMP]):
                    t = t.strip()
                    if len(t) > 2:
                        try:
                            httpr.urlopen(httpr.Request(SERVER_URL, data=t.encode("utf-8")))
                        except Exception as ex:
                            print("Error conectando con Kopter: ", ex)
                t2 = datetime.now()
                stream.start_stream()
                t3 = datetime.now()
                print(f"Tiempo total {t3 - t0}, guardar {t1 - t0}, asr {t2 - t1}, start {t3 - t2}", flush=True)

            if do_reset:
                print(f"(reset!)", flush=True)
                do_reset = False

            buff[:] = bytearray()
    except KeyboardInterrupt:
        print("Audio capture stopped.")
    finally:
        stream.stop_stream()
        stream.close()

if __name__ == "__main__":
    thread = threading.Thread(target=mq_http_server)
    thread.daemon = True
    thread.start()
    buff = bytearray()
    list_input_devices()
    audio_capture_thread(buff)
    p.terminate()

