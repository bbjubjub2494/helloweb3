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

from ctf_launchers.team_provider import TeamProvider
from ctf_launchers.types import (CreateInstanceRequest, DaemonInstanceArgs,
                                 LaunchAnvilInstanceArgs, UserData,
                                 get_player_account,)
from ctf_launchers.utils import deploy, get_web3

CHALLENGE = os.getenv("CHALLENGE", "challenge")
PUBLIC_HOST = os.getenv("PUBLIC_HOST", "http://127.0.0.1:1338")

TIMEOUT = int(os.getenv("TIMEOUT", "1440"))


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

    def get_daemon_instances(self) -> Dict[str, DaemonInstanceArgs]:
        return {}

    def get_instance_id(self) -> str:
        return f"chal-{CHALLENGE}-{self.team}".lower()

    def update_metadata(self, new_metadata: Dict[str, str]):
        self.metadata[self.team] = new_metadata
        pass

    def deploy_challenge(self) -> int:
        print("deploying challenge...")

        token = secrets.token_hex()
        datadir = os.path.join("/tmp/geths", token)

        # run geth in the background
        proc = subprocess.Popen(["geth", "-dev", "-datadir", datadir])
        time.sleep(1)

        # fund player account from dev account
        web3 = get_web3(token)
        web3.eth.send_transaction({
                "from": web3.eth.accounts[0],
                "to": get_player_account(self.mnemonic).address,
                "value": web3.to_wei(1, "ether"),
                })

        challenge_addr = self.deploy(self.mnemonic, token)

        self.update_metadata(
            {"mnemonic": self.mnemonic, "token": token, "challenge_address": challenge_addr}
        )

        print()
        print(f"your challenge has been deployed")
        print(f"---")
        print(f"rpc endpoint:       {PUBLIC_HOST}/{token}")
        print(f"private key:        {get_player_account(self.mnemonic).key.hex()}")
        print(f"challenge contract: {challenge_addr}")
        return 0

    def deploy(self, mnemonic: str, token: str) -> str:
        web3 = get_web3(token)

        return deploy(
            web3,
            token,
            self.project_location,
            mnemonic,
        )
