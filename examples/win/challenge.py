import asyncio

from helloweb3.pow import ChallengeWithAnvilAndPow
from helloweb3.pwn import PwnChallengeWithAnvil
from helloweb3.connection import Connection


class Challenge(PwnChallengeWithAnvil, ChallengeWithAnvilAndPow):
    pass



event_loop = asyncio.new_event_loop()

async def amain():
    async def client_connected_cb(reader, writer):
        with Connection(reader, writer) as conn:
            await Challenge.handle(conn)
    server = await asyncio.start_server(client_connected_cb, "0.0.0.0", 1337)
    await server.serve_forever()

event_loop.run_until_complete(amain())
