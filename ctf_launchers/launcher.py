import abc
import os
import shelve
import secrets
import traceback
import subprocess
import time
from dataclasses import dataclass
from typing import Callable, Dict, List

from eth_account.hdaccount import generate_mnemonic
from web3 import Web3

from ctf_launchers.team_provider import TeamProvider
from ctf_launchers.utils import deploy, get_player_account

PUBLIC_HOST = os.getenv("PUBLIC_HOST", "http://127.0.0.1:1338")
TIMEOUT = int(os.environ.setdefault("TIMEOUT", "60"))


@dataclass
class Action:
    name: str
    handler: Callable[[], int]


class Launcher(abc.ABC):
    def __init__(
        self, project_location: str, provider: TeamProvider, actions: List[Action] = []
    ):
        self.project_location = project_location
        self.__team_provider = provider

        self.metadata = shelve.open("metadata.db")

        self._actions = [
            Action(name="deploy challenge", handler=self.deploy_challenge),
        ] + actions

    @property
    def web3(self):
        return Web3(Web3.IPCProvider(os.path.join("/tmp/geths", self.token, "geth.ipc")))

    def run(self):
        self.team = self.__team_provider.get_team()
        if not self.team:
            exit(1)

        self.mnemonic = generate_mnemonic(12, lang="english")

        for i, action in enumerate(self._actions):
            print(f"{i+1} - {action.name}")

        try:
            handler = self._actions[int(input("action? ")) - 1]
        except:
            print("can you not")
            exit(1)

        try:
            status = handler.handler()
        except Exception as e:
            traceback.print_exc()
            print("an error occurred", e)
            status = 1
        finally:
            self.metadata.close()
        exit(status)

    def update_metadata(self, new_metadata: Dict[str, str]):
        self.metadata[self.team] = new_metadata
        pass

    def deploy_challenge(self) -> int:
        print("deploying challenge...")

        self.token = secrets.token_hex()
        datadir = os.path.join("/tmp/geths", self.token)

        # run geth in the background
        proc = subprocess.Popen(["challenge/with_timeout.sh", "geth", "-dev", "-datadir", datadir])
        while not os.access(os.path.join("/tmp/geths", token, "geth.ipc"), os.R_OK):
            time.sleep(1)

        # fund player account from dev account
        self.fund(get_player_account(self.mnemonic).address)

        challenge_addr = self.deploy()

        self.update_metadata(
            {"mnemonic": self.mnemonic, "token": self.token, "challenge_address": challenge_addr}
        )

        print()
        print(f"your challenge has been deployed")
        print(f"---")
        print(f"rpc endpoint:       {PUBLIC_HOST}/{self.token}")
        print(f"private key:        {get_player_account(self.mnemonic).key.hex()}")
        print(f"challenge contract: {challenge_addr}")
        return 0

    def fund(self, address):
        return self.web3.eth.send_transaction({
                "from": self.web3.eth.accounts[0],
                "to": address,
                "value": self.web3.to_wei(1, "ether"),
                })

    def deploy(self) -> str:
        return deploy(
            self.web3,
            self.token,
            self.project_location,
            self.mnemonic,
        )
