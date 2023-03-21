from os import environ

from http.server import BaseHTTPRequestHandler, HTTPServer

APP_HOST = ''
APP_PORT = int(environ.get('PORT', 8000))


class GetHandler(BaseHTTPRequestHandler):
    def _set_headers(self):
        self.send_response(204)
        self.end_headers()

    def do_GET(self):
        self._set_headers()


def run_server(handler_class=GetHandler):
    server_address = (APP_HOST, APP_PORT)
    httpd = HTTPServer(server_address, handler_class)
    httpd.serve_forever()
