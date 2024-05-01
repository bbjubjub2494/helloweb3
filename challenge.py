import socketserver

from lib.base import ChallengeBase


class Challenge(ChallengeBase):
    pass


with socketserver.ThreadingTCPServer(
    ("0.0.0.0", 1337), Challenge.make_handler_class()
) as server:
    server.serve_forever()
