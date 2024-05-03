from abc import *

import asyncio
import dataclasses
import os
import secrets
import socketserver
import typing

from eth_account.hdaccount import generate_mnemonic
from web3 import Web3

from .internal.util import TextStreamRequestHandler, deploy, get_player_account
from .internal.pow import Pow


PUBLIC_HOST = os.getenv("PUBLIC_HOST", "http://127.0.0.1:8545")
TIMEOUT = int(os.environ.setdefault("TIMEOUT", "60"))


@dataclasses.dataclass
class Action:
    description: str
    handler: typing.Callable[[], typing.Awaitable[None]]


class ChallengeBase(ABC, Pow, TextStreamRequestHandler):
    # per-subclass key value database to store challenge instance information
    metadata: dict[str, typing.Any]
    event_loop: asyncio.AbstractEventLoop
    token: str

    def update_metadata(self, new_metadata: dict[str, str]):
        self.metadata[self.token] = new_metadata

    @property
    def actions(self) -> list[Action]:
        return [
            Action("deploy", self._deploy_challenge),
            Action("say hello", self._say_hello),
        ]

    @property
    def web3(self):
        return Web3(
            Web3.IPCProvider(os.path.join("/tmp/geths", self.token, "geth.ipc"))
        )

    async def _say_hello(self) -> None:
        self.print("hello web3")

    async def request_token(self):
        token = self.input("token? ")
        if not token.isalnum():
            self.print("bad token")
            raise Exception("bad token")
        if token not in self.metadata:
            self.print("instance not found")
            raise Exception("instance not found")
        self.token = token

    async def _deploy_challenge(self):
        self.require_pow()

        self.print("deploying challenge...")

        self.mnemonic = generate_mnemonic(12, lang="english")
        self.token = secrets.token_hex()
        datadir = os.path.join("/tmp/geths", self.token)

        # run geth in the background
        geth = await asyncio.create_subprocess_exec("geth", "-dev", "-datadir", datadir)
        while not os.access(
            os.path.join("/tmp/geths", self.token, "geth.ipc"), os.R_OK
        ):
            await asyncio.sleep(1)

        try:
            async with asyncio.timeout(TIMEOUT):
                # fund player account from dev account
                await self.fund(get_player_account(self.mnemonic).address)

                challenge_addr = await self.deploy()

                self.update_metadata(
                    {"mnemonic": self.mnemonic, "challenge_address": challenge_addr}
                )

                self.print()
                self.print(f"your challenge has been deployed")
                self.print(f"it will be stopped in {TIMEOUT} seconds")
                self.print(f"---")
                self.print(f"token:              {self.token}")
                self.print(f"rpc endpoint:       {PUBLIC_HOST}/{self.token}")
                self.print(
                    f"private key:        {get_player_account(self.mnemonic).key.hex()}"
                )
                self.print(f"challenge contract: {challenge_addr}")
        finally:
            geth.terminate()
            await geth.wait()

    async def fund(self, address):
        tx = self.web3.eth.send_transaction(
            {
                "from": self.web3.eth.accounts[0],
                "to": address,
                "value": self.web3.to_wei(1, "ether"),
            }
        )
        return await asyncio.to_thread(self.web3.eth.wait_for_transaction_receipt, tx)

    async def deploy(self) -> str:
        return await asyncio.to_thread(
            deploy,
            self.web3,
            self.token,
            "contracts/",
            self.mnemonic,
        )

    def handle(self) -> None:
        for i, a in enumerate(self.actions):
            self.print(f"{i+1} - {a.description}")
        choice = self.input("> ")
        try:
            handler = self.actions[int(choice) - 1].handler
        except:
            self.print("ngmi")
        else:
            future = asyncio.run_coroutine_threadsafe(handler(), self.event_loop)
            future.result()

    @classmethod
    def make_handler_class(cls, event_loop) -> type[socketserver.BaseRequestHandler]:
        metadata: dict[str, typing.Any] = {}

        class RequestHandler(cls):
            def __init__(self, request, client_address, server) -> None:
                self.metadata = metadata
                self.event_loop = event_loop
                super().__init__(request, client_address, server)

        return RequestHandler
