import os
from http.server import HTTPServer, BaseHTTPRequestHandler

base_path = os.path.dirname(__file__)


class StaticServer(BaseHTTPRequestHandler):

    def do_GET(self):
        filename = 'reddit-2021111125211538.txt'

        self.send_response(200)
        self.send_header('Content-type', 'text/txt')
        self.end_headers()
        with open(os.path.join(base_path, filename), 'rb') as fh:
            self.wfile.write(fh.read())


def run(server_class=HTTPServer, handler_class=StaticServer, port=8000):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print('Starting Server on port {}'.format(port))
    httpd.serve_forever()


run()
