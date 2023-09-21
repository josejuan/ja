import pyaudio
import queue
import pprint

CHUNK_SECONDS = 1
SAMPLE_RATE = 44100
DEVICE_INDEX=11
TEMP='/tmp/microphone_transcribe.py.temp.wav'

CHUNK_SIZE = SAMPLE_RATE * CHUNK_SECONDS

p = pyaudio.PyAudio()

# Use `arecord -D hw:2,0 --dump-hw-params` to get supported sample rates...
# Test using `aplay -r 16000 -f S32_LE microphone_transcribe.py.temp.wav`

def list_input_devices():
    device_count = p.get_device_count()
    print("Available input devices:")
    for i in range(device_count):
        device_info = p.get_device_info_by_index(i)
        if device_info['maxInputChannels'] > 0:
            print(f"Index {i}: {device_info['name']}")

def audio_capture_thread(buff):
    stream = p.open(
        format=pyaudio.paInt16,
        # format=pyaudio.paInt32,
        channels=1,
        rate=SAMPLE_RATE,
        input=True,
        #output=True,
        frames_per_buffer=CHUNK_SIZE,
        input_device_index=DEVICE_INDEX
    )
    try:
        for x in range(0, 10):
            print("Captured...", flush=True)
            audio_chunk = stream.read(CHUNK_SIZE)
            buff.extend(audio_chunk)
        with open(TEMP, "wb") as f:
            f.write(buff)
        print("Done.")
    except KeyboardInterrupt:
        print("Audio capture stopped.")
    finally:
        stream.stop_stream()
        stream.close()

if __name__ == "__main__":
    buff = bytearray()
    list_input_devices()
    audio_capture_thread(buff)
    p.terminate()

