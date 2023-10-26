
import time
import ssl
import base64
import pyaudio
import queue
from websocket import create_connection

CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100

# Initialize the PyAudio
p = pyaudio.PyAudio()

# Start recording - replace with real code below please
stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK)

print("* Recording...")

# Create a queue for buffering
buffer_queue = queue.Queue()

# Sign the request to AWS - replace with real data please :D 
# signed_url = sign_request(aws_credentials, 'transcribestreaming', region)
signed_url = "SIGNED_URL_HERE"

# WebSocket connection stuff
def connect_websocket():
    return create_connection(signed_url,
                             sslopt={"cert_reqs": ssl.CERT_NONE},
                             subprotocols=["binary", "base64"])

ws = None

try:
    while True:
        data = stream.read(CHUNK)

        # If webSocket is not connected, buffer that data
        if ws is None or not ws.connected:
            buffer_queue.put(data)
            if ws is None:
                try:
                    ws = connect_websocket()
                    print("* WebSocket connected Woot!")
                except:
                    print("* Still waiting for WebSocket connection...")
                    time.sleep(2)  # Waiting 2 long seconds before retrying
        else:
            # Sending the buffered data first.. hopeuflly no loss
            while not buffer_queue.empty():
                ws.send_binary(buffer_queue.get())
            
            ws.send_binary(data)

            # Get the transcription result... brief version - replace with whatever code is needed below :)
            result = ws.recv()
            print(result)

except KeyboardInterrupt:
    print("* Done recording")
    if ws:
        ws.close()
    stream.stop_stream()
    stream.close()
    p.terminate()
