import asyncio
import os
import secrets

from eth_account.hdaccount import generate_mnemonic
from web3 import Web3

from .internal.util import deploy, get_player_account
from .internal.pow import Pow
from .base import Action, ChallengeBase


PUBLIC_HOST = os.getenv("PUBLIC_HOST", "http://127.0.0.1:8545")
TIMEOUT = int(os.environ.setdefault("TIMEOUT", "60"))


class ChallengeWithAnvil(ChallengeBase, Pow):
    def actions(self) -> list[Action]:
        return [
            Action("deploy", self._deploy_challenge),
        ]

    @property
    def web3(self):
        return Web3(Web3.IPCProvider(os.path.join("/tmp/anvils", self.token)))

    async def _request_token(self):
        token = await self.input("token? ")
        if not token.isalnum():
            await self.print("bad token")
            raise Exception("bad token")
        if token not in self.metadata:
            await self.print("instance not found")
            raise Exception("instance not found")
        self.token = token

    async def _deploy_challenge(self):
        await self.require_pow()

        await self.print("deploying challenge...")

        self.mnemonic = generate_mnemonic(12, lang="english")
        self.token = secrets.token_hex()
        os.makedirs("/tmp/anvils", exist_ok=True)
        ipc_path = os.path.join("/tmp/anvils", self.token)

        # run anvil in the background
        anvil = await asyncio.create_subprocess_exec(
            "anvil", "--port", "0", "--ipc", ipc_path, "-m", self.mnemonic
        )

        try:
            async with asyncio.timeout(TIMEOUT):
                while not os.access(ipc_path, os.R_OK):
                    await asyncio.sleep(1)

                challenge_addr = await asyncio.to_thread(
                    deploy,
                    self.web3,
                    self.token,
                    "contracts/",
                    self.mnemonic,
                )

                await self.put_metadata(
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
            anvil.terminate()
            await anvil.wait()
