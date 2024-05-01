from abc import *

import asyncio
import dataclasses
import socketserver
import typing

from . import util


@dataclasses.dataclass
class ChallengeBase(util.TextStreamRequestHandler, ABC):
    # per-subclass key value database to store challenge instance information
    metadata: dict[str, typing.Any]

    def __init__(self, request, client_address, server) -> None:
        super().__init__(request, client_address, server)

    async def ahandle(self) -> None:
        self.print("hello web3")

    def handle(self) -> None:
        loop = asyncio.new_event_loop()
        loop.run_until_complete(self.ahandle())

    @classmethod
    def make_handler_class(cls) -> type[socketserver.BaseRequestHandler]:
        metadata: dict[str, typing.Any] = {}

        class RequestHandler(cls):
            def __init__(self, request, client_address, server) -> None:
                super().__init__(request, client_address, server)
                self.metadata = metadata

        return RequestHandler
