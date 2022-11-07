from DHServer import DHHTTPHandler
from http.server import HTTPServer
import json
import requests
import threading


class DiffieHellman:
    def __init__(self, ip, port, name, p=0, g=0):
        self.ip = ip
        self.port = port
        self.name = name
        self.p = p
        self.g = g

        server_address = (self.ip, self.port)
        self.httpd = HTTPServer(server_address, DHHTTPHandler)
        self.server_thread = threading.Thread(target=self.run_server)

    def start(self):
        self.server_thread.start()

    def stop(self):
        self.httpd.server_close()
        self.server_thread.join()

    def send_request(self, address):
        url = f"http://{address[0]}:{address[1]}/"
        data = {"name": self.name}
        r = requests.post(url, json=data)
        print(r.text)
        # return r.json()

    def run_server(self):
        self.httpd.serve_forever()


def main():
    ui = input("(A)lice or (B)ob: ")
    if ui.lower() == "a":
        DH = DiffieHellman("127.0.0.1", 8000, "Alice")
    elif ui.lower() == "b":
        DH = DiffieHellman("127.0.0.1", 8001, "Bob")
    else:
        print("Invalid input")
        return

    DH.start()

    while True:
        ui = input("(Q)uit or (S)end: ")
        if ui.lower() == "q":
            DH.stop()
            break
        elif ui.lower() == "s":
            if DH.name == "Alice":
                DH.send_request(("127.0.0.1", 8001))
            else:
                DH.send_request(("127.0.0.1", 8000))


if __name__ == '__main__':
    main()
