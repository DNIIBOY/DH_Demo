from ControlPanel import ControlPanel
from encyption import Encryption

from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import requests
import sys
import threading


class DHHTTPHandler(BaseHTTPRequestHandler):
    def __init__(self, request, client_address, server):
        super().__init__(request, client_address, server)

    def _set_response(self):
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()

    def do_POST(self) -> None:
        """
        Handles POST requests
        """
        content_length = int(self.headers["Content-Length"])  # Gets the size of data
        post_data = self.rfile.read(content_length)  # Gets the data itself
        post_data = json.loads(post_data.decode("utf-8"))  # Parse as json
        response = DH.receive_request(post_data)  # Pass data to DH and get response

        self._set_response()
        self.wfile.write(json.dumps(response).encode("utf-8"))  # Send response


class DiffieHellman:
    def __init__(self, port=8080, name="", g=-1, p=-1, secret=-1, public=-1, remote_public=-1, shared_secret=-1, remote_ip="", remote_port=8080):
        self.port = port  # Port to run the server on
        self._name = name  # Name of the user, Alice or Bob
        self.g = g  # Shared generator g
        self.p = p  # Shared prime p
        self.secret = secret  # Own secret key
        self.public = public  # Own public key
        self.remote_public = remote_public  # Remote public key
        self.shared_secret = shared_secret  # Shared key K
        self.remote_ip = remote_ip  # IP of the remote user
        self.remote_port = remote_port  # Port of the remote user

        self.httpd = None  # HTTP server, gets initialized in start()
        self.server_thread = threading.Thread(target=self.run_server)  # Thread for the HTTP server

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value) -> None:
        """
        Update the name of the user, and change which port to run the server on
        """
        self._name = value
        value = value.lower()
        if value == "alice":
            self.port = 8000
            self.remote_port = 8001
        elif value == "bob":
            self.port = 8001
            self.remote_port = 8000

    @property
    def remote_name(self) -> str:
        """
        :return: Expected name of the remote user
        """
        if self.name.lower() == "alice":
            return "Bob"
        elif self.name.lower() == "bob":
            return "Alice"
        return ""

    def calculate_public_key(self) -> int:
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
        """
        Send a request to the remote user
        :param request_type: 'shared' for the shared parameters, 'public' for the public key
        :return:
        """
        url = f"http://{self.remote_ip}:{self.remote_port}/"  # URL to send the request to
        data = {"name": self.name}  # Always send the name of the user, so we don't get two users with the same name

        match request_type:
            case "shared":  # Send the shared parameters
                data["type"] = "shared"
                data["g"] = self.g
                data["p"] = self.p
            case "public":  # Send the public key
                data["type"] = "public"
                data["public"] = self.public
            case "start_chat":
                data["type"] = "set_state"
                data["state"] = "messaging"
            case _:
                return False

        print("Sending request: ", data)
        try:
            r = requests.post(url, json=data).json()  # Send the data
        except requests.exceptions.ConnectionError:  # If the connection failed
            print("Connection error")
            return False
        return r["success"]

    def send_message(self, message) -> bool:
        """
        Send a message to the remote user
        :param message: The message to send
        :return: True if the message was sent successfully, False otherwise
        """
        print(f"Sending message to {self.remote_name}")
        url = f"http://{self.remote_ip}:{self.remote_port}/"  # URL to send the message to
        enc = Encryption(self.shared_secret)  # Encryption object
        enc_msg, tag, nonce = enc.encrypt(message)  # Encrypt the message
        data = {"name": self.name, "type": "message", "message": enc_msg, "tag": tag, "nonce": nonce}  # Create the data to send
        try:
            r = requests.post(url, json=data).json()  # Send the data
            return r["success"]  # Return whether the request was successful
        except requests.exceptions.ConnectionError:  # If the connection failed
            print("Connection error")
            return False

    def receive_request(self, data) -> dict:
        """
        Receive a request from the remote user
        :param data: The request data
        :return: The JSON response
        """
        try:
            print("Received request: ", data)  # Print the received data
            response = {"name": self.name, "success": False}  # Create a response, success is False until updated

            # Check if the request is from the expected sender, does not help for security, but is nice to have
            if data["name"].lower() != self.remote_name.lower():
                response["error"] = f"Wrong name, expected {self.remote_name}"
                return response

            match data["type"]:  # Match the type of the request
                case "shared":  # If the request is for the shared parameters
                    if "g" not in data or "p" not in data:  # Check if the parameters are present
                        response["error"] = "Missing parameters"
                        return response  # Return response, if parameters are missing
                    self.p = data["p"]  # Set the shared parameters
                    self.g = data["g"]
                    CP.receive_shared(self.p, self.g)  # Update the control panel
                    response["success"] = True  # Set success as True

                case "public":  # If the request contains other party's public key
                    if "public" not in data:  # Check if the public key is present
                        response["error"] = "Missing parameters"
                        return response  # Return response, if public key is missing

                    self.remote_public = data["public"]  # Set the remote public key value
                    if self.public != -1:  # If we have our own public key, calculate the shared secret
                        self.calculate_shared_secret()
                    CP.receive_public(self.remote_public)  # Update the control panel with the remote public key

                    # Status is pending, if we have not yet created our own public key
                    response["status"] = "pending" if self.public == -1 else "complete"
                    if response["status"] == "complete":
                        response["public"] = self.public  # Send our public key, if we have already created it
                    response["success"] = True

                case "set_state":  # Request to change the state of the client
                    if "state" not in data:  # Check if the parameter is present
                        response["error"] = "Missing parameters"
                        return response
                    try:
                        CP.state = data["state"]  # Set the state of the control panel
                    except Exception as e:
                        response["error"] = str(e)
                        return response
                    response["success"] = True

                case "message":  # If the request contains a message
                    if "message" not in data or "tag" not in data or "nonce" not in data:  # Check if all parameters are present
                        response["error"] = "Missing parameters"
                        return response  # Return response, if parameters are missing
                    enc = Encryption(self.shared_secret)  # Create an encryption object
                    msg = enc.decrypt(data["message"], data["tag"], data["nonce"])  # Decrypt the message
                    CP.receive_message(msg)  # Update the control panel with the message
                    response["success"] = True

                case _:
                    response["error"] = "Invalid request type, expected 'shared', 'public' or 'message'"  # If the request type is invalid
            return response

        except Exception as e:
            # If an error occurs, return a response with success as False
            return {"name": self.name, "success": False, "error": str(e)}

    def start(self) -> None:
        """
        Start the server
        """
        server_address = ("", self.port)
        print("Starting server on ", server_address)
        self.httpd = HTTPServer(server_address, DHHTTPHandler)
        self.server_thread.start()

    def stop(self) -> None:
        """
        Stop the server
        """
        try:
            self.httpd.shutdown()
            self.server_thread.join(2)
        except (AttributeError, RuntimeError):  # If the server is not running
            pass

    def run_server(self) -> None:
        """
        Function to run the server in a thread
        """
        self.httpd.serve_forever()

    @staticmethod
    def reset():
        reset()


def reset():
    global DH
    global CP
    print("Resetting...")
    DH.stop()
    DH = DiffieHellman(remote_ip=DH.remote_ip)
    CP.DH = DH
    CP.name_label.config(text="")  # Reset the name label
    CP.state = 0


def main():
    global DH
    global CP

    remote_ip = "127.0.0.1"
    if len(sys.argv) > 1:
        remote_ip = sys.argv[1]

    DH = DiffieHellman(remote_ip=remote_ip)
    CP = ControlPanel(DH)
    CP.start()

    DH.stop()
    print("Exiting...")


if __name__ == "__main__":
    DH: DiffieHellman = None
    CP: ControlPanel = None
    main()
