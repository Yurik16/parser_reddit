import json
import os
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from io import BytesIO

base_path = os.path.dirname(__file__)
RESULT = [
    "key", "value",
]


class StaticServer(BaseHTTPRequestHandler):
    RESULT_FILENAME = ''
    RESULT = [
        "key", "value",
    ]

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

    def _set_headers(self, content='text/html'):
        self.send_response(200)
        self.send_header('Content-type', content, )
        self.end_headers()

    def do_GET(self):
        # Getting str after last '/' in curl
        uid = self.requestline.split(' ')[1].split('/')[-1]
        if self.path == '/json/':
            filename = 'result.json'
            self._set_headers('application/json')
            with open(os.path.join(base_path, filename), 'rb') as fh:
                self.wfile.write(fh.read())
        elif self.path == '/wait':
            self._set_headers()
            self.wfile.write(self._html("Waiting ..."))
        elif self.path == '/':
            self._set_headers()
            self.wfile.write(self.list_to_html_table(RESULT, 2).encode("utf8"))
        elif self.path == f'/posts/{uid}':
            filename = f'reddit-{self.RESULT_FILENAME}.json'
            self._set_headers('application/json')
            with open(os.path.join(base_path, filename), 'rb') as fh:
                self.wfile.write(fh.readlines()[int(uid.encode("utf8"))])
        elif self.path == f'/get_url/{uid}':
            self._set_headers('application/json')
            self.wfile.write(self._html(self.requestline))

    def do_POST(self):
        if self.path == '/posts/':
            if self.RESULT_FILENAME == '':
                time_str = str(datetime.now().strftime("%Y%m%D%H%M").replace("/", ""))
                self.RESULT_FILENAME = f'reddit-{time_str}.json'
            self._set_headers('application/json')
            content_length = int(self.headers['Content-length'])
            body = self.rfile.read(content_length)
            with open(f'{self.RESULT_FILENAME}', 'a') as file:
                file.write(body.decode("utf-8") + "\n")


def run(server_class=HTTPServer, handler_class=StaticServer, port=8000):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print('Starting Server on port {}'.format(port))
    httpd.serve_forever()


run()
