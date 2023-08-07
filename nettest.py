import http.server
import socketserver
import threading
# import urllib.request as httpr

HTTP_IP="0.0.0.0"
HTTP_PORT=9057
SERVER_URL='http://192.168.0.31:9057'

class MqRequestHandler(http.server.BaseHTTPRequestHandler):
    def do_POST(self):
        text = self.rfile.read(int(self.headers['Content-Length'])).decode('utf-8')
        print(f"$$ recibido: {text}")
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'Ok')

def mq_http_server():
    print(f"Starting web server on {HTTP_IP}:{HTTP_PORT}")
    with socketserver.TCPServer((HTTP_IP, HTTP_PORT), MqRequestHandler) as s:
        s.serve_forever()

thread = threading.Thread(target=mq_http_server)
thread.daemon = True
thread.start()

while True:
    pass
