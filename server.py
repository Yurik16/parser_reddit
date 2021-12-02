import json
import os
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from io import BytesIO

base_path = os.path.dirname(__file__)


class StaticServer(BaseHTTPRequestHandler):
    RESULT_FILENAME = ''
    time_str = str(datetime.now().strftime("%Y%m%D").replace("/", ""))

    def _html(self, message: str):
        """Generates an HTML document that includes `message`
        in the body.
        """
        content = f"<html><body><h1>{message}</h1></body></html>"
        return content.encode("utf8")

    def row_major(self, alist: list, sublen: int) -> list:
        return [alist[i:i + sublen] for i in range(0, len(alist), sublen)]

    def col_major(self, alist: list, sublen: int) -> list:
        num_rows = (len(alist) + sublen - 1) // sublen
        return [alist[i::sublen] for i in range(num_rows)]

    def html_table(self, lst: list) -> iter:
        yield '<table>'
        for sublist in lst:
            yield '  <tr><td>'
            yield '    </td><td>'.join(sublist)
            yield '  </td></tr>'
        yield '</table>'

    def list_to_html_table(self, alist: list, sublength: int, column_major=False) -> str:
        """Generate html table
        :param alist: list
        :param sublength: number of elements in col/row
        :param column_major: boolean col or row
        :return: string with html-table
        """
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
        uid = self.requestline.split(' ')[1].split('/')[-1]
        if self.path == '/json/':
            filename = 'result.json'
            self._set_headers('application/json')
            with open(os.path.join(base_path, filename), 'rb') as fh:
                self.wfile.write(fh.read())
        elif self.path == '/wait':
            self._set_headers()
            self.wfile.write(self._html("Waiting ..."))
        elif self.path =='/posts/':
            self._set_headers('application/json')
            filename = f'reddit-{self.time_str}.json'
            with open(os.path.join(base_path, filename), 'rb') as fh:
                for each in fh:
                    self.wfile.write(each)
                    self.wfile.write(f'\n'.encode("utf-8"))
        elif self.path == f'/posts/{uid}':
            filename = f'reddit-{self.time_str}.json'
            self._set_headers('application/json')
            with open(os.path.join(base_path, filename), 'rb') as fh:
                self.wfile.write(fh.readlines()[int(uid.encode("utf8"))])
        elif self.path == f'/get_url/{uid}':
            self._set_headers('application/json')
            self.wfile.write(self._html(self.requestline))

    def do_POST(self):
        if self.path == '/posts/':
            self._set_headers('application/json')
            content_length = int(self.headers['Content-length'])
            body = self.rfile.read(content_length)
            with open(f'reddit-{self.time_str}.json', 'a') as file:
                file.write(body.decode("utf-8") + "\n")
            uid = body.decode("utf-8").split('": {')[0][2::]
            self.wfile.write(self._html(uid))



def run(server_class=HTTPServer, handler_class=StaticServer, port=8000):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print('Starting Server on port {}'.format(port))
    httpd.serve_forever()


run()
