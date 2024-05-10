import asyncio
import contextlib
import os
import secrets

from eth_account.hdaccount import generate_mnemonic
from web3 import Web3

from .internal.util import deploy, get_player_account
from .actions import Action
from .base import ChallengeBase


PUBLIC_HOST = os.getenv("PUBLIC_HOST", "http://127.0.0.1:8545")
TIMEOUT = int(os.environ.setdefault("TIMEOUT", "60"))


class ChallengeWithAnvil(ChallengeBase):
    instances = {}
    token: str

    def __init__(self, token: str):
        self.token = token

    @classmethod
    def actions(cls):
        deploy_action = Action("deploy", cls._deploy)
        return [deploy_action]

    @property
    def web3(self):
        return Web3(Web3.IPCProvider(os.path.join("/tmp/anvils", self.token)))

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

        self.mnemonic = generate_mnemonic(12, lang="english")
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
            await conn.print(f"your challenge has been deployed")
            await conn.print(f"it will be stopped in {TIMEOUT} seconds")
            await conn.print(f"---")
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
