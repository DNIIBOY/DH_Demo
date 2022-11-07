from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import os
import requests
import threading


class DHHTTPHandler(BaseHTTPRequestHandler):
    def __init__(self, request, client_address, server):
        super().__init__(request, client_address, server)
        self.received_data = {}

    def _set_response(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])  # Gets the size of data
        post_data = self.rfile.read(content_length)  # Gets the data itself
        post_data = json.loads(post_data.decode('utf-8'))  # Parse as json
        response = DH.parse_request(post_data)

        self._set_response()
        self.wfile.write(json.dumps(response).encode('utf-8'))  # Send response


class DiffieHellman:
    def __init__(self, ip, port, name, g=-1, n=-1, secret=-1):
        self.ip = ip
        self.port = port
        self.name = name
        self.g = g
        self.n = n
        self.secret = secret

        server_address = (self.ip, self.port)
        self.httpd = HTTPServer(server_address, DHHTTPHandler)
        self.server_thread = threading.Thread(target=self.run_server)

    def start(self):
        self.server_thread.start()

    def stop(self):
        self.httpd.shutdown()
        self.server_thread.join()

    def send_request(self, address):
        url = f"http://{address[0]}:{address[1]}/"
        data = {"name": self.name}
        r = requests.post(url, json=data)
        print(r.text)
        # return r.json()

    def parse_request(self, data):
        response = {"name": self.name, "success": False}

        if data["name"] == self.name:
            return response

        match data["type"]:
            case "shared":
                self.g = data["g"]
                self.n = data["n"]
                response["success"] = True
            case "public":
                pass
            case _:
                pass
        os.system("cls")
        return response

    def run_server(self):
        self.httpd.serve_forever()


if __name__ == "__main__":
    try:
        ui = input("(A)lice or (B)ob: ")
        match ui.lower():
            case "a":
                DH = DiffieHellman("127.0.0.1", 8000, "Alice")
            case "b":
                DH = DiffieHellman("127.0.0.1", 8001, "Bob")
            case _:
                print("Invalid input")

        DH.start()

        while True:
            ui = input("(Q)uit or (S)end: ")
            if ui.lower() == "q":
                break
            elif ui.lower() == "s":
                if DH.name == "Alice":
                    DH.send_request(("127.0.0.1", 8001))
                else:
                    DH.send_request(("127.0.0.1", 8000))

    except KeyboardInterrupt:
        pass
    except:
        DH.stop()
        raise

    DH.stop()
