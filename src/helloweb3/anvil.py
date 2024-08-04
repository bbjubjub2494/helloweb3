import asyncio
import contextlib
import os
import secrets
from typing import ClassVar, Self

from eth_account.hdaccount import generate_mnemonic
from web3 import AsyncWeb3, Web3

from .internal.util import deploy, get_player_account
from .actions import Action
from .base import ChallengeBase


PUBLIC_HOST = os.getenv("PUBLIC_HOST", "http://127.0.0.1:8545")
TIMEOUT = int(os.environ.setdefault("TIMEOUT", "60"))

Token = str

class ChallengeWithAnvil(ChallengeBase):
    """
    A challenge that must be solved on a fresh Anvil instance.
    Each instance is identified by a server-generated random token.

    Note that this module is tightly-coupled with the template.

    This requires an RPC proxy like the rpc_proxy module to sit between the player and the Anvil instance.

    The $PUBLIC_HOST environment variable will be given to the user as the base address of the proxy.
    After $TIMEOUT seconds, the instance will be destroyed.
    """
    instances: ClassVar[dict[Token, Self]] = {}
    token: Token

    def __init__(self, token: Token):
        self.challenge_addr = None
        self.mnemonic = generate_mnemonic(12, lang="english")
        self.token = token

    @classmethod
    def actions(cls):
        deploy_action = Action("deploy", cls._deploy)
        return [deploy_action]

    @property
    def web3(self):
        return Web3(Web3.IPCProvider(os.path.join("/tmp/anvils", self.token)))

    @property
    def async_web3(self):
        return AsyncWeb3(Web3.AsyncHTTPProvider(f"http://127.0.0.1:8545/{self.token}"))

    @classmethod
    async def _deploy(cls, conn):
        token = secrets.token_hex()
        chal = cls(token)
        cls.instances[token] = chal
        try:
            await chal.deploy(conn)
        finally:
            del cls.instances[token]

    async def deploy(self, conn):
        await conn.print("deploying challenge...")

        os.makedirs("/tmp/anvils", exist_ok=True)
        ipc_path = os.path.join("/tmp/anvils", self.token)

        async with asyncio.timeout(TIMEOUT), background_subprocess_exec(
            "anvil", "--port", "0", "--ipc", ipc_path, "-m", self.mnemonic
        ):
            # wait for anvil start
            while not os.access(ipc_path, os.R_OK):
                await asyncio.sleep(1)

            self.challenge_addr = await asyncio.to_thread(
                deploy,
                self.web3,
                self.token,
                "contracts/",
                self.mnemonic,
            )

            await conn.print()
            await conn.print("your challenge has been deployed")
            await conn.print(f"it will be stopped in {TIMEOUT} seconds")
            await conn.print("---")
            await conn.print(f"token:              {self.token}")
            await conn.print(f"rpc endpoint:       {PUBLIC_HOST}/{self.token}")
            await conn.print(
                f"private key:        {get_player_account(self.mnemonic).key.hex()}"
            )
            await conn.print(f"challenge contract: {self.challenge_addr}")
            # continue in the background from now on
            conn.close()
            await asyncio.sleep(TIMEOUT)


@contextlib.asynccontextmanager
async def background_subprocess_exec(*argv):
    proc = await asyncio.create_subprocess_exec(*argv)
    try:
        yield proc
    finally:
        proc.terminate()
        await proc.wait()
