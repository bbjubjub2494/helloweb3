from abc import *

import asyncio
import dataclasses
import os
import io
import secrets
import socketserver
import typing

from eth_account.hdaccount import generate_mnemonic
from web3 import Web3

from .internal.util import deploy, get_player_account
from .internal.pow import Pow


PUBLIC_HOST = os.getenv("PUBLIC_HOST", "http://127.0.0.1:8545")
TIMEOUT = int(os.environ.setdefault("TIMEOUT", "60"))


@dataclasses.dataclass
class Action:
    description: str
    handler: typing.Callable[[], typing.Awaitable[None]]


class ChallengeBase(ABC, Pow):
    # per-subclass key value database to store challenge instance information
    metadata: dict[str, typing.Any]
    token: str

    def __init__(self, reader, writer, metadata):
        self._reader = reader
        self._writer = writer
        self.metadata = metadata

    async def print(self, *args, sep=" ", end="\n", flush=False):
        buf = io.StringIO()
        print(*args, sep=sep, end=end, file=buf, flush=flush)
        self._writer.write(buf.getvalue().encode())
        await self._writer.drain()

    async def input(self, prompt=""):
        self._writer.write(prompt.encode())
        await self._writer.drain()
        return (await self._reader.readline()).strip()

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
        await self.print("hello web3")

    async def request_token(self):
        token = await self.input("token? ")
        if not token.isalnum():
            await self.print("bad token")
            raise Exception("bad token")
        if token not in self.metadata:
            await self.print("instance not found")
            raise Exception("instance not found")
        self.token = token

    async def _deploy_challenge(self):
        self.require_pow()

        await self.print("deploying challenge...")

        self.mnemonic = generate_mnemonic(12, lang="english")
        self.token = secrets.token_hex()
        datadir = os.path.join("/tmp/geths", self.token)

        # run geth in the background
        geth = await asyncio.create_subprocess_exec("geth", "-dev", "-datadir", datadir)

        try:
            async with asyncio.timeout(TIMEOUT):
                while not os.access(
                    os.path.join("/tmp/geths", self.token, "geth.ipc"), os.R_OK
                ):
                    await asyncio.sleep(1)
                # fund player account from dev account
                await self.fund(get_player_account(self.mnemonic).address)

                challenge_addr = await self.deploy()

                self.update_metadata(
                    {"mnemonic": self.mnemonic, "challenge_address": challenge_addr}
                )

                await self.print()
                await self.print(f"your challenge has been deployed")
                await self.print(f"it will be stopped in {TIMEOUT} seconds")
                await self.print(f"---")
                await self.print(f"token:              {self.token}")
                await self.print(f"rpc endpoint:       {PUBLIC_HOST}/{self.token}")
                await self.print(
                    f"private key:        {get_player_account(self.mnemonic).key.hex()}"
                )
                await self.print(f"challenge contract: {challenge_addr}")
                await asyncio.sleep(TIMEOUT)
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

    async def prompt_action(self) -> Action:
        actions = self.actions
        if len(actions) == 0:
            return Action("say hello", self._say_hello)
        elif len(actions) == 1:
            return actions[0]
        for i, a in enumerate(actions):
            await self.print(f"{i+1} - {a.description}")
        while True:
            try:
                choice = int(await self.input("> "))
            except ValueError:
                continue
            if 1 <= choice <= len(actions):
                return actions[choice - 1]

    async def handle(self) -> None:
        action = await self.prompt_action()
        await action.handler()
