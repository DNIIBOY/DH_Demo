import threading
import multiprocessing
import time
import sys

from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlparse
import json


class RequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urlparse(self.path)
        params = parse_qs(parsed_path.query)
        self.send_response(200)
        self.end_headers()
        process.kill()

        self.wfile.write(json.dumps({
            'method': self.command,
            'params': params,
            'request_version': self.request_version,
            'protocol_version': self.protocol_version,
        }).encode())
        return


def test_function():
    while True:
        print("test")
        time.sleep(1)


process = multiprocessing.Process(target=test_function)

if __name__ == '__main__':
    server = HTTPServer(('localhost', 8080), RequestHandler)
    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.daemon = True
    server_thread.start()
    print('Server loop running in thread:', server_thread.name)
    process.start()

    while True:
        time.sleep(1)
