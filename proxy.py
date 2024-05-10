from http.server import *
import http
import web3
import json
import os.path
import posixpath
import re


class HTTPRequestHandler(BaseHTTPRequestHandler):
    # allow standard methods and otterscan
    # in particular, don't allow cheatcodes
    _ALLOW = re.compile(r'^(eth|ots)_')

    def do_POST(self):
        length = int(self.headers.get("Content-Length"))
        message = json.loads(self.rfile.read(length))
        method, params = message["method"], message.get("params")
        token = posixpath.normpath(self.path).lstrip("/")
        ipc_path = os.path.join("/tmp/anvils", token)

        if not _ALLOW.search(method):
            self.send_error(http.HTTPStatus.NOT_ALLOWED, "forbidden RPC method")
            return

        provider = web3.IPCProvider(ipc_path)
        response = json.dumps(provider.make_request(method, params))

        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(response.encode())


ThreadingHTTPServer(("", 8545), HTTPRequestHandler).serve_forever()
