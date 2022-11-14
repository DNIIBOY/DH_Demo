from ControlPanel import ControlPanel
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
    def __init__(self, port=8080, name="", g=-1, p=-1, secret=-1, public=-1, remote_public=-1, shared_secret=-1, remote_ip="", remote_port=8080):
        self.port = port
        self._name = name
        self.other_name = "Alice" if name == "Bob" else "Bob"
        self.g = g
        self.p = p
        self.secret = secret
        self.public = public
        self.remote_public = remote_public
        self.shared_secret = shared_secret
        self.remote_ip = remote_ip
        self.remote_port = remote_port

        self.httpd = None  # HTTP server, gets initialized in start()
        self.server_thread = threading.Thread(target=self.run_server)  # Thread for the HTTP server

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value
        value = value.lower()
        if value == "alice":
            self.port = 8000
            self.remote_port = 8001
        elif value == "bob":
            self.port = 8001
            self.remote_port = 8000

    def send_request(self, request_type: str) -> bool:
        url = f"http://{self.remote_ip}:{self.remote_port}/"
        data = {"name": self.name}

        match request_type:
            case "shared":
                data["type"] = "shared"
                data["g"] = self.g
                data["p"] = self.p
                r = requests.post(url, json=data).json()
                return r["success"]  # Return True, if successful
            case "public":
                data["type"] = "public"
                data["public"] = self.public
                r = requests.post(url, json=data).json()
                if r["success"]:
                    if r["status"] == "complete":  # If the remote has already decided on a public key
                        self.remote_public = r["public"]
                        CP.get_public(self.remote_public)

                    return True  # Return True, if successful

            case _:
                return False

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
                    CP.get_shared(self.p, self.g)
                except KeyError:
                    response["error"] = "Missing parameters"
                    return response
                response["success"] = True

            case "public":
                try:
                    self.remote_public = data["public"]
                    CP.get_public(self.remote_public)
                    response["status"] = "awaiting" if CP.state == "pick_private" else "complete"
                    if response["status"] == "complete":
                        response["public"] = self.public
                except KeyError:
                    response["error"] = "Missing parameters"
                    return response
                response["success"] = True

            case _:
                response["error"] = "Invalid request type"

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
    global CP
    CP.start()

    DH.stop()
    print("Exiting...")


if __name__ == "__main__":
    DH = DiffieHellman(remote_ip="192.168.1.37")
    CP = ControlPanel(DH)
    main()
