import asyncio
import socketserver

from lib.anvil import ChallengeWithAnvil


class Challenge(ChallengeWithAnvil):
    pass



event_loop = asyncio.new_event_loop()

async def amain():
    metadata = {}
    async def client_connected_cb(reader, writer):
        handler = Challenge(reader, writer, metadata)
        await handler.handle()
    server = await asyncio.start_server(client_connected_cb, "0.0.0.0", 1337)
    await server.serve_forever()

event_loop.run_until_complete(amain())
