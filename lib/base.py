from abc import *

import socketserver
import typing


class ChallengeBase(socketserver.StreamRequestHandler, ABC):
    @property
    @abstractmethod
    def metadata(self) -> dict[str, typing.Any]:
        """key value database to store instance information"""
        pass

    def handle(self) -> None:
        self.wfile.write(b"hello web3\n")

    @classmethod
    def make_handler_class(cls) -> type[socketserver.StreamRequestHandler]:
        metadata: dict[str, typing.Any] = {}  # global variable

        class RequestHandler(cls):
            @property
            def metadata(self):
                return metadata

        return RequestHandler
