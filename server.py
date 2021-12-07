import os
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler

base_path = os.path.dirname(__file__)


class StaticServer(BaseHTTPRequestHandler):
    """Simple HTTP server with CRUD operations. """
    time_str = str(datetime.now().strftime('%Y_%m_%d'))
    RESULT_FILENAME = f'reddit_{time_str}.txt'

    def _set_headers(self, content='text/html'):
        """Setting header to the headers buffer"""
        self.send_response(200)
        self.send_header('Content-type', content, )
        self.end_headers()

    def do_GET(self):
        """Handle GET request"""
        # save digits following by last '/' as variable
        row = self.path.split('/')[-1]
        if self.path == '/posts/':
            self._set_headers('application/json')
            with open(os.path.join(base_path, self.RESULT_FILENAME), 'rb') as fh:
                for each in fh:
                    self.wfile.write(each)
                    self.wfile.write(f'\n'.encode("utf-8"))
        elif self.path == f'/posts/{row}':
            self._set_headers('application/json')
            with open(os.path.join(base_path, self.RESULT_FILENAME), 'rb') as fh:
                # write to response body row number 'row' from file handler 'fh'
                try:
                    self.wfile.write(fh.readlines()[int(row.encode("utf-8"))])
                except IndexError as ie:
                    self.wfile.write((f'no entry - {ie}').encode("utf-8"))
                    self.send_response(404)

    def do_POST(self):
        """Handle POST request and saving body to txt file"""
        if self.path == '/posts/':
            self._set_headers('application/json')
            content_length = int(self.headers['Content-length'])
            body = self.rfile.read(content_length)
            # gets unique id by splitting body/row and missing first 2 symbols
            uid = body.decode("utf-8").split(';')[0][2::]
            with open(self.RESULT_FILENAME, 'a+') as file:
                # change position of cursor to start of file
                file.seek(0)
                # save to variable whole file as a string
                file_as_str = file.read()
                # finding coincidence - is uid-string in file
                if file_as_str.find(uid) != -1:
                    self.wfile.write((f'{uid} - duplicates are restricted').encode("utf-8"))
                    self.send_response(301)
                    return
                file.write(body.decode("utf-8") + ",\n")
                # finding coincidence counts instead counting rows
                lines_count = file_as_str.count("],\n")
                self.wfile.write((f'{uid}: {lines_count}').encode("utf-8"))
                self.send_response(201)

    def do_DELETE(self):
        """Handle DELETE request"""
        # save digits following by last '/' as variable
        line_num = self.path.split('/')[-1]
        if self.path == f'/posts/{line_num}':
            self._set_headers('application/json')
            with open(self.RESULT_FILENAME, 'r+') as file:
                # change position of cursor to start of file
                file.seek(0)
                # gets list of entries
                lines = file.readlines()
                # checking is there a given number among of entries
                if int(line_num) not in range(0, len(lines)):
                    self.wfile.write((f'entry {line_num} - is missing').encode("utf-8"))
                    self.send_response(404)
                    return
                # change position of cursor to start of file
                file.seek(0)
                # cut file to cursor - erase all data
                file.truncate()
                # recreate all file from lines variable but without entry what needs to delete
                for enum, line in enumerate(lines):
                    if enum != int(line_num):
                        file.write(line)
                self.wfile.write((f'entry {line_num} - now deleted').encode("utf-8"))
                self.send_response(201)

    def do_PUT(self):
        """Handle PUT request. Replace pointed entry with given body request"""
        # save digits following by last '/' as variable
        uid = self.path.split('/')[-1]
        if self.path == f'/posts/{uid}':
            self._set_headers('application/json')
            content_length = int(self.headers['Content-length'])
            body = self.rfile.read(content_length)
            with open(self.RESULT_FILENAME, 'r+') as file:
                # change position of cursor to start of file
                file.seek(0)
                # save to variable whole file as a string
                file_as_str = file.read()
                # checking is uid look like uuid and finding coincidence - is uid-string in file
                if len(uid) > 35 and file_as_str.find(uid) != -1:
                    file.seek(0)
                    # gets list of entries
                    lines = file.readlines()
                    file.seek(0)
                    file.truncate()
                    # recreate all file from lines variable and replace looking uid/entry with given body
                    for line in lines:
                        if line.find(uid) != -1:
                            file.write(body.decode("utf-8") + ",\n")
                        else:
                            file.write(line)
                    self.wfile.write((f'entry uid - {uid} - updated').encode("utf-8"))
                    self.send_response(201)
                else:
                    self.wfile.write((f'{uid} - there is no such uid at {self.RESULT_FILENAME}').encode("utf-8"))
                    self.send_response(404)


def run(server_class=HTTPServer, handler_class=StaticServer, port=8000):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print('Starting Server on port {}'.format(port))
    httpd.serve_forever()


run()
