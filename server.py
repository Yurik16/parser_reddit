import argparse
import json
import os
import socketserver
from collections import namedtuple
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from typing import Tuple

from AbcDatabase import AbcDatabase
from db_postgre import PostgreDB

base_path = os.path.dirname(__file__)


class StaticServer(BaseHTTPRequestHandler):
    """Simple HTTP server with CRUD operations. """
    time_str = str(datetime.now().strftime('%Y_%m_%d'))
    RESULT_FILENAME = f'reddit_{time_str}.txt'

    def __init__(self, request: bytes, client_address: Tuple[str, int],
                 server: socketserver.BaseServer):
        self.args = self.argparse_init()

        if self.args.database == 'postgre':
            self.abstractDB = PostgreDB()
        # elif self.args.database == 'mongo':
        #     self.abstractDB = MongoDB()
        super(StaticServer, self).__init__(request, client_address, server)

    @staticmethod
    def argparse_init(database='postgre') -> "args":
        """Init argparse module
        :param database: source database
        :return: argparse module object
        """
        parser = argparse.ArgumentParser()
        parser.add_argument("--database", metavar="database", type=str, default=database,
                            help="'postgre' or 'mongo' - what database to use? default 'postgre'")
        parser.add_argument("--port", metavar="port", type=int, default=8000,
                            help="what port to use for HTTPserver")
        args = parser.parse_args()
        return args

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
            result_list = self.abstractDB.get_all_entry()
            for each in result_list:
                self.wfile.write(each.encode("utf-8"))
                self.wfile.write(f'\n'.encode("utf-8"))
        elif self.path == f'/posts/{url_end}':
            self._set_headers('application/json')
            try:
                result_str = self.abstractDB.get_one_entry(url_end)
                self.wfile.write(result_str.encode('utf-8'))
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
            all_vars = get_all_sending_variables(body)
            self.abstractDB.insert_user(*all_vars.user_atr)
            self.abstractDB.insert_post(uid, *all_vars.post_atr)
            self.wfile.write((f'{uid}: {self.abstractDB.get_one_entry(uid)}').encode("utf-8"))

    def do_DELETE(self):
        """Handle DELETE request"""
        # save digits following by last '/' as variable
        uid = self.path.split('/')[-1]
        if self.path == f'/posts/{uid}':
            self._set_headers()
            self.abstractDB.delete_post(uid)
            self.wfile.write((f'entry {uid} - now deleted').encode("utf-8"))
            self.send_response(201)

    def do_PUT(self):
        """Handle PUT request. Replace pointed entry with given body request"""
        # save digits following by last '/' as variable
        uid = self.path.split('/')[-1]
        if self.path == f'/posts/{uid}' and is_uid(uid) and self.is_uid_in_data(uid):
            self._set_headers('application/json')
            content_length = int(self.headers['Content-length'])
            body = self.rfile.read(content_length)
            all_vars = get_all_sending_variables(body)
            self.abstractDB.update_user(uid, *all_vars.user_atr)
            self.abstractDB.update_post(uid, *all_vars.post_atr)
            self.wfile.write((f'entry uid - {uid} - updated').encode("utf-8"))
            self.send_response(201)
        else:
            self.wfile.write((f'{uid} - there is no such uid at {self.RESULT_FILENAME}').encode("utf-8"))
            self.send_response(404)

    def is_uid_in_data(self, var: str) -> bool:
        all_entry = self.abstractDB.get_all_entry()
        is_var_in = sum(len(elem) for elem in all_entry if elem.find(var) > -1)
        return is_var_in > 0


def is_uid(var: str) -> bool:
    return (len(var) == 36) and (len(var.split("-")) == 5)


def get_all_sending_variables(body: bytes) -> namedtuple:
    body_value = dict(list(json.loads(body).values())[0])
    # filter user`s attributes from request body
    user_atr = [val for key, val in body_value.items() if key.find("user_") != -1]
    # filter post`s attributes from request body
    post_atr = [val for key, val in body_value.items() if key.find("post_") != -1 or key.find("user_name") == 0]
    Variables = namedtuple('Variables', ['user_atr', 'post_atr'])
    return Variables(user_atr, post_atr)


def run(handler_class=StaticServer, server_class=HTTPServer, port=8000):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print('Starting Server on port {}'.format(port))
    httpd.serve_forever()


if __name__ == '__main__':
    run()
