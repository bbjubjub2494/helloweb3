import io
import socketserver


class TextStreamRequestHandler(socketserver.StreamRequestHandler):
    def setup(self):
        super().setup()
        self.wfile = io.TextIOWrapper(self.wfile)
        self.rfile = io.TextIOWrapper(self.rfile)

    def print(self, *args, sep=" ", end="\n", flush=False):
        print(*args, sep=sep, end=end, file=self.wfile, flush=flush)

    def input(self, prompt=""):
        self.wfile.write(prompt)
        self.wfile.flush()
        return self.rfile.readline().strip()
