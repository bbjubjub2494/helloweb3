import abc
import os
import shelve
import secrets
import traceback
import subprocess
import sys
import time
import hashlib
from dataclasses import dataclass
from typing import Callable, Dict, List

from eth_account.hdaccount import generate_mnemonic
from web3 import Web3

from ctf_launchers.utils import deploy, get_player_account

PUBLIC_HOST = os.getenv("PUBLIC_HOST", "http://127.0.0.1:8545")
TIMEOUT = int(os.environ.setdefault("TIMEOUT", "60"))

# copied from: https://github.com/balsn/proof-of-work
class NcPowser:
    def __init__(self, difficulty=22, prefix_length=16):
        self.difficulty = difficulty
        self.prefix_length = prefix_length

    def get_challenge(self):
        return secrets.token_urlsafe(self.prefix_length)[:self.prefix_length].replace('-', 'b').replace('_', 'a')

    def verify_hash(self, prefix, answer):
        h = hashlib.sha256()
        h.update((prefix + answer).encode())
        bits = ''.join(bin(i)[2:].zfill(8) for i in h.digest())
        return bits.startswith('0' * self.difficulty)

@dataclass
class Action:
    name: str
    handler: Callable[[], int]


class Launcher(abc.ABC):
    def __init__(
        self, project_location: str, actions: List[Action] = []
    ):
        self.project_location = project_location

        self.metadata = shelve.open("metadata.db")

        self._actions = [
            Action(name="deploy challenge", handler=self.deploy_challenge),
        ] + actions

    @property
    def web3(self):
        return Web3(Web3.IPCProvider(os.path.join("/tmp/geths", self.token, "geth.ipc")))

    def run(self):
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
            exit(1)
        finally:
            self.metadata.close()
        exit(0)

    def update_metadata(self, new_metadata: Dict[str, str]):
        self.metadata[self.token] = new_metadata
        pass

    def request_token(self):
        token = input("token? ")
        if not token.isalnum():
            print("bad token")
            exit(1)
        if token not in self.metadata:
            print("instance not found")
            exit(1)
        self.token = token

    def deploy_challenge(self):
        powser = NcPowser()
        prefix = powser.get_challenge()
        print(f"please : sha256({prefix} + ???) == {'0'*powser.difficulty}({powser.difficulty})... ")
        print(f"prefix: {prefix}")
        print(f"difficulty: {powser.difficulty}")
        sys.stdout.flush()
        answer = input(" >")
        if not powser.verify_hash(prefix, answer):
            print("no etherbase for you")
            exit(0)

        print("deploying challenge...")

        self.mnemonic = generate_mnemonic(12, lang="english")
        self.token = secrets.token_hex()
        datadir = os.path.join("/tmp/geths", self.token)

        # run geth in the background
        proc = subprocess.Popen(["challenge/with_timeout.sh", "geth", "-dev", "-datadir", datadir])
        while not os.access(os.path.join("/tmp/geths", self.token, "geth.ipc"), os.R_OK):
            time.sleep(1)

        # fund player account from dev account
        self.fund(get_player_account(self.mnemonic).address)

        challenge_addr = self.deploy()

        self.update_metadata(
            {"mnemonic": self.mnemonic, "challenge_address": challenge_addr}
        )

        print()
        print(f"your challenge has been deployed")
        print(f"---")
        print(f"token:              {self.token}")
        print(f"rpc endpoint:       {PUBLIC_HOST}/{self.token}")
        print(f"private key:        {get_player_account(self.mnemonic).key.hex()}")
        print(f"challenge contract: {challenge_addr}")

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
