from http.server import BaseHTTPRequestHandler, HTTPServer
import json


class DHHTTPHandler(BaseHTTPRequestHandler):
    def _set_response(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])  # Gets the size of data
        post_data = self.rfile.read(content_length)  # Gets the data itself
        post_data = json.loads(post_data.decode('utf-8'))  # Parse as json
        print(post_data)

        self._set_response()
        self.wfile.write(f"POST request for {self.path}".encode('utf-8'))  # Send response


def run(port=8000):
    server_address = ('', port)
    httpd = HTTPServer(server_address, DHHTTPHandler)
    print('Starting httpd...\n')
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    print('Stopping httpd...\n')


if __name__ == '__main__':
    from sys import argv

    if len(argv) == 2:
        run(port=int(argv[1]))
    else:
        run()
