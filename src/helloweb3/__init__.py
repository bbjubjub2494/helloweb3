"""
# Web3 CTF framework
"""


from .base import ChallengeBase
from .anvil import ChallengeWithAnvil
from .internal.util import PlayerError
from .pwn import PwnChallengeWithAnvil
from .pow import ChallengeWithAnvilAndPow

async def serve_challenge(cls: type[ChallengeBase], host="0.0.0.0", port=1337):
    """
    Listen on a TCP socket for player connections and present the provided challenge, until interrupted.
    """
    import asyncio

    from .actions import handle_with_actions
    from .connection import Connection

    async def client_connected_cb(reader, writer):
        with Connection(reader, writer) as conn:
            try:
                await handle_with_actions(conn, cls.actions())
            except PlayerError as e:
                await conn.print(e)
            except asyncio.TimeoutError:
                pass # silence
    server = await asyncio.start_server(client_connected_cb, host, port)

    await server.serve_forever()
