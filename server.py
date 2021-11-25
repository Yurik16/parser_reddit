import os
from http.server import HTTPServer, BaseHTTPRequestHandler

base_path = os.path.dirname(__file__)


class StaticServer(BaseHTTPRequestHandler):

    def do_GET(self):
        filename = 'result.json'

        self.send_response(200)
        self.send_header('Content-type', 'text/json')
        self.end_headers()
        with open(os.path.join(base_path, filename), 'rb') as fh:
            self.wfile.write(fh.read())

    def do_POST(self):
        rr = self.
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        # content_length = ??
        # wfile -

        self.end_headers()
        self.data_string = self.rfile.read(int(self.headers['Content-Length']))

        data = b'<html><body><h1>POST!</h1></body></html>'
        self.wfile.write(bytes(data))
        return


def run(server_class=HTTPServer, handler_class=StaticServer, port=8000):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print('Starting Server on port {}'.format(port))
    httpd.serve_forever()


run()
