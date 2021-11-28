import json
import os
from io import BytesIO
from http.server import HTTPServer, BaseHTTPRequestHandler

base_path = os.path.dirname(__file__)


class StaticServer(BaseHTTPRequestHandler):

    def _html(self, message):
        """Generates an HTML document that includes `message`
        in the body.
        """
        content = f"<html><body><h1>{message}</h1></body></html>"
        return content.encode("utf8")

    def do_GET(self):
        if self.path == '/json':
            filename = 'result.json'
            self.send_response(200)
            self.send_header('Content-type', 'application/json', )
            self.end_headers()
            with open(os.path.join(base_path, filename), 'rb') as fh:
                self.wfile.write(fh.read())
        elif self.path == '/wait':
            self.send_response(200)
            self.send_header('Content-type', 'text/html', )
            self.end_headers()
            self.wfile.write(self._html("Waiting ..."))

    def do_POST(self):
        content_length = int(self.headers['Content-length'])
        body = self.rfile.read(content_length)
        self.send_response(200)
        self.send_header('Content-type', 'text/html', )
        self.end_headers()
        response = BytesIO()
        response.write(b'new data gets to list')
        response.write(body)
        self.wfile.write(response.getvalue())


def run(server_class=HTTPServer, handler_class=StaticServer, port=8000):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print('Starting Server on port {}'.format(port))
    httpd.serve_forever()


run()
