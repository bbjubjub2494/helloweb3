from abc import *

import asyncio
import dataclasses
import socketserver
import typing

from . import util


@dataclasses.dataclass
class Action:
    description: str
    handler: typing.Callable[[], typing.Awaitable[None]]


class ChallengeBase(util.TextStreamRequestHandler, ABC):
    # per-subclass key value database to store challenge instance information
    metadata: dict[str, typing.Any]
    event_loop: asyncio.AbstractEventLoop

    @property
    def actions(self) -> list[Action]:
        return [
            Action("say hello", self._say_hello),
        ]

    async def _say_hello(self) -> None:
        self.print("hello web3")

    def handle(self) -> None:
        for i, a in enumerate(self.actions):
            self.print(f"{i+1} - {a.description}")
        choice = self.input("> ")
        try:
            handler = self.actions[int(choice)-1].handler
        except:
            self.print("ngmi")
            return
        future = asyncio.run_coroutine_threadsafe(handler(), self.event_loop)
        return future.result()

    @classmethod
    def make_handler_class(cls, event_loop) -> type[socketserver.BaseRequestHandler]:
        metadata: dict[str, typing.Any] = {}

        class RequestHandler(cls):
            def __init__(self, request, client_address, server) -> None:
                self.metadata = metadata
                self.event_loop = event_loop
                super().__init__(request, client_address, server)

        return RequestHandler
