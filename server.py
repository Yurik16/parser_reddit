import json
import os
from io import BytesIO
from http.server import HTTPServer, BaseHTTPRequestHandler

base_path = os.path.dirname(__file__)
RESULT = [
    "key", "value",
]


class StaticServer(BaseHTTPRequestHandler):

    def _html(self, message):
        """Generates an HTML document that includes `message`
        in the body.
        """
        content = f"<html><body><h1>{message}</h1></body></html>"
        return content.encode("utf8")

    def row_major(self, alist, sublen):
        return [alist[i:i + sublen] for i in range(0, len(alist), sublen)]

    def col_major(self, alist, sublen):
        numrows = (len(alist) + sublen - 1) // sublen
        return [alist[i::sublen] for i in range(numrows)]

    def html_table(self, lst):
        yield '<table>'
        for sublist in lst:
            yield '  <tr><td>'
            yield '    </td><td>'.join(sublist)
            yield '  </td></tr>'
        yield '</table>'

    def list_to_html_table(self, alist, sublength, column_major=False):
        if column_major:
            lol = self.col_major(alist, sublength)
        else:
            lol = self.row_major(alist, sublength)
        return ''.join(self.html_table(lol))

    def do_GET(self):
        if self.path == '/json/':
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
        elif self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html', )
            self.end_headers()
            self.wfile.write(self.list_to_html_table(RESULT, 2).encode("utf8"))

    def do_POST(self):
        content_length = int(self.headers['Content-length'])
        body = self.rfile.read(content_length)
        self.send_response(200)
        RESULT.append(body.decode("utf8"))
        self.send_header('Content-type', 'text/html', )
        self.send_header('Content-type', 'application/json', )
        self.end_headers()
        response = BytesIO()
        response.write(b'new data gets to list:\n')
        response.write(body)
        self.wfile.write(response.getvalue())


def run(server_class=HTTPServer, handler_class=StaticServer, port=8000):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print('Starting Server on port {}'.format(port))
    httpd.serve_forever()


run()
