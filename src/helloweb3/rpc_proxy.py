"""
Listen for HTTP RPC requests on port 8545 and pass them on to running ChallengeWithAnvil instances.
"""


from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import http
import web3
import json
import os.path
import posixpath
import re


class ForbiddenMethod(Exception):
    pass


class HTTPRequestHandler(BaseHTTPRequestHandler):
    # allow standard methods and otterscan
    # in particular, don't allow cheatcodes
    _ALLOW = re.compile(r'^(eth|erigon|ots)_')

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Request-Method", "POST")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_POST(self):
        length = int(self.headers.get("Content-Length"))
        message = json.loads(self.rfile.read(length))
        try:
            if isinstance(message, list):
                response = [self._handle_rpc(message) for message in message]
            else:
                response = self._handle_rpc(message)
        except ForbiddenMethod as e:
            self.send_error(http.HTTPStatus.FORBIDDEN, e.args[0])
            return

        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(response).encode())

    def _handle_rpc(self, message):
        method, params, id_ = message["method"], message.get("params"), message.get("id")
        token = posixpath.normpath(self.path).lstrip("/")
        ipc_path = os.path.join("/tmp/anvils", token)

        if not self._ALLOW.search(method):
            raise ForbiddenMethod(f"forbidden RPC method: {method}")

        provider = web3.IPCProvider(ipc_path)
        response = provider.make_request(method, params)
        response['id'] = id_
        return response


if __name__ == '__main__':
    ThreadingHTTPServer(("", 8545), HTTPRequestHandler).serve_forever()
