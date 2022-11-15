from ControlPanel import ControlPanel
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import requests
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

    @property
    def other_name(self):
        if self.name.lower() == "alice":
            return "Bob"
        elif self.name.lower() == "bob":
            return "Alice"
        return ""

    def calculate_public(self) -> int:
        """
        Calculates the public key, based on the secret key and the shared parameters
        :return: The public key
        """
        self.public = pow(self.g, self.secret, self.p)
        return self.public

    def calculate_shared_secret(self) -> int:
        """
        Calculates the shared secret, based on the remote public key and the shared parameters
        :return: The shared secret.
        """
        self.shared_secret = pow(self.remote_public, self.secret, self.p)
        return self.shared_secret

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
                data["public"] = self.public
            case _:
                return False

        print("Sending request: ", data)
        r = requests.post(url, json=data).json()
        return r["success"]  # Return True, if successful

    def receive_request(self, data):
        try:
            print("Received request: ", data)  # Print the received data
            response = {"name": self.name, "success": False}  # Create a response, success is False by default

            # Check if the request is from the expected sender, does not help for security, but is nice to have
            if data["name"].lower() != self.other_name.lower():
                response["error"] = f"Wrong name, expected {self.other_name}"
                return response

            match data["type"]:  # Match the type of the request
                case "shared":  # If the request is for the shared parameters
                    if "g" not in data or "p" not in data:  # Check if the parameters are present
                        response["error"] = "Missing parameters"
                        return response  # Return response, if parameters are missing
                    self.p = data["p"]  # Set the shared parameters
                    self.g = data["g"]
                    CP.get_shared(self.p, self.g)  # Update the control panel
                    response["success"] = True  # Set success as True
                case "public":  # If the request contains other party's public key
                    if "public" not in data:  # Check if the public key is present
                        response["error"] = "Missing parameters"
                        return response  # Return response, if public key is missing

                    self.remote_public = data["public"]  # Set the remote public key value
                    if self.public != -1:  # If we have our own public key, calculate the shared secret
                        self.calculate_shared_secret()
                    CP.get_public(self.remote_public)  # Update the control panel with the remote public key

                    # Respond if we are waiting for the other party's public key or if we have both public keys
                    response["status"] = "awaiting" if CP.state == "pick_private" else "complete"
                    if response["status"] == "complete":
                        response["public"] = self.public  # Send our public key, if we have both public keys
                    response["success"] = True
                case _:
                    response["error"] = "Invalid request type, expected 'shared' or 'public'"  # If the request type is invalid
            return response

        except:
            # If an error occurs, return a response with success as False
            return {"name": self.name, "success": False, "error": "Internal server error"}
            raise

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
    DH = DiffieHellman(remote_ip="127.0.0.1")
    CP = ControlPanel(DH)
    main()
