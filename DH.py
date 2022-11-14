from UIHandler import UIHandler
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import os
import requests
import sys
import threading


class DHHTTPHandler(BaseHTTPRequestHandler):
    def __init__(self, request, client_address, server):
        super().__init__(request, client_address, server)

    def _set_response(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()

    def do_POST(self):
        content_length = int(self.headers["Content-Length"])  # Gets the size of data
        post_data = self.rfile.read(content_length)  # Gets the data itself
        post_data = json.loads(post_data.decode("utf-8"))  # Parse as json
        response = DH.receive_request(post_data)

        self._set_response()
        self.wfile.write(json.dumps(response).encode("utf-8"))  # Send response


class DiffieHellman:
    def __init__(self, port=8080, name="", g=-1, p=-1, secret=-1, public=-1, shared_secret=-1, remote_ip="", remote_port=8081):
        self.port = port
        self.name = name
        self.g = g
        self.p = p
        self.secret = secret
        self.public = public
        self.shared_secret = shared_secret
        self.remote_ip = remote_ip
        self.remote_port = remote_port

        self.httpd = None  # HTTP server, gets initialized in start()
        self.server_thread = threading.Thread(target=self.run_server)  # Thread for the HTTP server

    def send_request(self, request_type: str) -> bool:
        url = f"http://{self.remote_ip}:{self.remote_port}/"
        data = {"name": self.name}

        match request_type:
            case "shared":
                data["type"] = "shared"
                data["g"] = self.g
                data["p"] = self.p
            case "public":
                data["type"] = "public"
            case _:
                return False

        r = requests.post(url, json=data)
        return r.json()["success"]  # Check if successful response

    def receive_request(self, data):
        global main_thread
        response = {"name": self.name, "success": False}

        if data["name"] == self.name:
            return response

        match data["type"]:
            case "shared":
                try:
                    self.p = data["p"]
                    self.g = data["g"]
                except KeyError:
                    response["error"] = "Missing parameters"
                    return response
                response["success"] = True

                main_thread.join()
                main_thread = threading.Thread(target=state2)
                main_thread.start()
                UIH.state = 2

            case "public":
                pass
            case _:
                pass

        return response

    def start(self):
        server_address = ("", self.port)
        print("Starting server on ", server_address)
        self.httpd = HTTPServer(server_address, DHHTTPHandler)
        self.server_thread.start()

    def stop(self):
        self.httpd.shutdown()
        self.server_thread.join(2)

    def run_server(self):
        self.httpd.serve_forever()


def main():
    global DH
    global main_thread

    main_thread.start()


if __name__ == "__main__":
    DH = DiffieHellman(port=8000, remote_ip="127.0.0.1")
    UIH = UIHandler(DH)
    main_thread = threading.Thread(target=state0)
    main()
