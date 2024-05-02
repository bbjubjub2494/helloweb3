import asyncio
import socketserver
import threading

from lib.base import ChallengeBase


class Challenge(ChallengeBase):
    pass



event_loop = asyncio.new_event_loop()
with socketserver.ThreadingTCPServer(
    ("0.0.0.0", 1337), Challenge.make_handler_class(event_loop)
) as server:
    t = threading.Thread(target=event_loop.run_forever)
    t.start()
    try:
        server.serve_forever()
    finally:
        event_loop.stop()
        t.join()
