from http.server import *
import web3
import json
import os.path
import posixpath


class HTTPRequestHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        length = int(self.headers.get("Content-Length"))
        message = json.loads(self.rfile.read(length))
        method, params = message['method'], message.get('params')
        path = os.path.join("/tmp/geths/", posixpath.normpath(self.path).lstrip('/'), "geth.ipc")
        self.log_message("path %s", path)
        self.log_message("req %s,%s", method, params)

        provider = web3.IPCProvider(path)
        response = json.dumps(provider.make_request(method, params))
        self.log_message("response %s", response)

        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(response.encode())

ThreadingHTTPServer(('', 1338), HTTPRequestHandler).serve_forever()
