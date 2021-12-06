import json
import os
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from io import BytesIO

base_path = os.path.dirname(__file__)


class StaticServer(BaseHTTPRequestHandler):
    time_str = str(datetime.now().strftime('%Y_%m_%d'))
    RESULT_FILENAME = f'reddit_{time_str}.txt'

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
        uid = self.path.split('/')[-1]
        if self.path == '/json/':
            self._set_headers('application/json')
            with open(os.path.join(base_path, self.RESULT_FILENAME), 'rb') as fh:
                self.wfile.write(fh.read())
        elif self.path == '/wait':
            self._set_headers()
            self.wfile.write(self._html("Waiting ..."))
        elif self.path == '/posts/':
            self._set_headers('application/json')
            with open(os.path.join(base_path, self.RESULT_FILENAME), 'rb') as fh:
                for each in fh:
                    self.wfile.write(each)
                    self.wfile.write(f'\n'.encode("utf-8"))
        elif self.path == f'/posts/{uid}':
            self._set_headers('application/json')
            with open(os.path.join(base_path, self.RESULT_FILENAME), 'rb') as fh:
                self.wfile.write(fh.readlines()[int(uid.encode("utf8"))])
        elif self.path == f'/get_url/{uid}':
            self._set_headers('application/json')
            self.wfile.write(self._html(self.requestline))

    def do_POST(self):
        if self.path == '/posts/':
            self._set_headers('application/json')
            content_length = int(self.headers['Content-length'])
            body = self.rfile.read(content_length)
            uid = body.decode("utf-8").split('": {')[0].strip()
            with open(self.RESULT_FILENAME, 'a+') as file:
                file_as_str = file.read()
                if file_as_str.find(uid) != -1:
                    self.wfile.write((f'{uid} - duplicates are restricted').encode("utf8"))
                    self.send_response(301)
                    return
                file.write(body.decode("utf-8"))
                sub = '": {'
                self.wfile.write((f'{uid}: {file_as_str.count(sub)}').encode("utf8"))

    def do_DELETE(self):
        line_num = self.path.split('/')[-1]
        if self.path == f'/posts/{line_num}':
            self._set_headers('application/json')
            with open(self.RESULT_FILENAME, 'r+') as fh:
                lines = fh.readlines()
                fh.seek(0)
                fh.truncate()
                for enum, line in enumerate(lines):
                    if enum != int(line_num):
                        fh.write(line)

    def do_PUT(self):
        line_num = self.path.split('/')[-1]
        if self.path == f'/posts/{line_num}':
            self._set_headers('application/json')
            content_length = int(self.headers['Content-length'])
            body = self.rfile.read(content_length)
            with open(f'reddit-{self.time_str}.json', 'r+') as fh:
                lines = fh.readlines()
                fh.seek(0)
                fh.truncate()
                for enum, line in enumerate(lines):
                    if enum != int(line_num):
                        fh.write(line)
                    else:
                        fh.write(body.decode("utf-8") + "\n")


def run(server_class=HTTPServer, handler_class=StaticServer, port=8000):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print('Starting Server on port {}'.format(port))
    httpd.serve_forever()


run()
