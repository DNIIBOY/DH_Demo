from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlparse
import json
import requests


class DiffieHellman:
    def __init__(self, ip, port, name, p=0, g=0):
        self.ip = ip
        self.port = port
        self.name = name
        self.p = p
        self.g = g


class RequestHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        parsed_path = urlparse(self.path)
        params = parse_qs(parsed_path.query)
        self.send_response(200)
        self.end_headers()

        self.wfile.write(json.dumps({
            'method': self.command,
            'params': params,
            'request_version': self.request_version,
            'protocol_version': self.protocol_version,
        }).encode())
        return


def main():
    alice = DiffieHellman("127.0.0.1", 8000, "Alice")
    bob = DiffieHellman("127.0.0.1", 8001, "Bob")


if __name__ == '__main__':
    main()
