import json
import os
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from db_postgre import PostgreDB

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
        url_end = self.path.split('/')[-1]
        if self.path == '/posts/':
            self._set_headers('application/json')
            with open(os.path.join(base_path, self.RESULT_FILENAME), 'r') as fh:
                for each in fh:
                    self.wfile.write(each.encode("utf-8"))
                    self.wfile.write(f'\n'.encode("utf-8"))
        elif self.path == f'/posts/row/{url_end}':
            self._set_headers('application/json')
            with open(os.path.join(base_path, self.RESULT_FILENAME), 'r') as fh:
                # write to response body row number 'row' from file handler 'fh'
                try:
                    self.wfile.write(fh.readlines()[int(url_end)].encode("utf-8"))
                    self.send_response(201)
                except (ValueError, IndexError) as ie:
                    self.wfile.write((f'no entry - {ie}').encode("utf-8"))
                    self.send_response(404)
        elif self.path == f'/posts/{url_end}':
            self._set_headers('application/json')
            with open(os.path.join(base_path, self.RESULT_FILENAME), 'r') as fh:
                try:
                    any_list = [line for line in fh if line.find(url_end) != -1]
                    self.wfile.write(any_list[0].encode("utf-8"))
                    self.send_response(201)
                except (ValueError, IndexError) as ie:
                    self.wfile.write((f'no entry - {ie}').encode("utf-8"))
                    self.send_response(404)

    def do_POST(self):
        """Handle POST request and saving body to txt file"""
        if self.path == '/posts/':
            self._set_headers('application/json')
            content_length = int(self.headers['Content-length'])
            body = self.rfile.read(content_length)
            # get unique id by deserialize body and pick "data"-key
            uid = "".join(json.loads(body).keys())
            body_value = dict(list(json.loads(body).values())[0])
            body_loads = json.loads(body)
            str_type = str(type(json.loads(body).values()))
            pg_database = PostgreDB()
            pg_database.create_table_users()
            pg_database.create_table_posts()
            # filter user`s attributes from request body
            user_atr = [val for key, val in body_value.items() if key.find("user_") != -1]
            # filter post`s attributes from request body
            post_atr = [val for key, val in body_value.items() if key.find("post_") != -1 or key.find("user_name") == 0]
            pg_database.insert_user(*user_atr)
            pg_database.insert_post(uid, *post_atr)
            self.wfile.write((f'{uid}: {body_value}').encode("utf-8"))

    def do_DELETE(self):
        """Handle DELETE request"""
        # save digits following by last '/' as variable
        uid = self.path.split('/')[-1]
        if self.path == f'/posts/{uid}':
            self._set_headers()
            with open(self.RESULT_FILENAME, 'r+') as file:
                if not self.is_uid_in_file(uid):
                    self.wfile.write((f'entry {uid} - is missing').encode("utf-8"))
                    self.send_response(404)
                    return
                # change position of cursor to start of file
                file_as_list = file.readlines()
                file.seek(0)
                # cut file to cursor - erase all data
                file.truncate()
                # recreate all file but without entry what needs to delete
                for line in file_as_list:
                    if line.find(uid) == -1:
                        file.write(line)
                self.wfile.write((f'entry {uid} - now deleted').encode("utf-8"))
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
                if self.is_uid(uid) and self.is_uid_in_file(uid):
                    # change position of cursor to start of file
                    file_as_list = file.readlines()
                    file.seek(0)
                    # cut file to cursor - erase all data
                    file.truncate()
                    # recreate all file from lines variable and replace looking uid/entry with given body
                    for line in file_as_list:
                        if line.find(uid) != -1:
                            file.write(body.decode("utf-8") + ",\n")
                        else:
                            file.write(line)
                    self.wfile.write((f'entry uid - {uid} - updated').encode("utf-8"))
                    self.send_response(201)
                else:
                    self.wfile.write((f'{uid} - there is no such uid at {self.RESULT_FILENAME}').encode("utf-8"))
                    self.send_response(404)

    @staticmethod
    def get_list_from_dict(data: dict) -> str:
        """Convert dict to string
        :param data: dict with parsing data
        :return: None
        """
        # logging.info("Convert data to list")
        result_str = "".join(f'{key};' +
                             f' https://www.reddit.com/{val["post_link"]};' +
                             f' {val["username"]};' +
                             f' {val["total_karma"]};' +
                             f' {val["cake_day"]};' +
                             f' {val["link_karma"]};' +
                             f' {val["comment_karma"]};' +
                             f' {val["post_date"]};' +
                             f' {val["Number_of_comments"]};' +
                             f' {val["post_votes"]};' +
                             f' {val["post_category"]};'
                             for key, val in data.items()
                             )
        return result_str

    @staticmethod
    def is_uid(var: str) -> bool:
        return (len(var) == 36) and (len(var.split("-")) == 5)

    def is_uid_in_file(self, var: str) -> bool:
        with open(self.RESULT_FILENAME, "r") as file:
            file_as_str = file.read()
            return file_as_str.find(var) > -1


def run(server_class=HTTPServer, handler_class=StaticServer, port=8000):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print('Starting Server on port {}'.format(port))
    httpd.serve_forever()


run()
