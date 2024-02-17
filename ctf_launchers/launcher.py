import abc
import os
import shelve
import traceback
from dataclasses import dataclass
from typing import Callable, Dict, List

import requests
from eth_account.hdaccount import generate_mnemonic

from ctf_launchers.team_provider import TeamProvider
from ctf_launchers.types import (CreateInstanceRequest, DaemonInstanceArgs,
                                 LaunchAnvilInstanceArgs, UserData,
                                 get_player_account,)
from ctf_launchers.utils import deploy, get_web3

CHALLENGE = os.getenv("CHALLENGE", "challenge")
PUBLIC_HOST = os.getenv("PUBLIC_HOST", "http://127.0.0.1:8545")

ETH_RPC_URL = os.getenv("ETH_RPC_URL")
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

    def get_anvil_instances(self) -> Dict[str, LaunchAnvilInstanceArgs]:
        return {
            "main": self.get_anvil_instance(),
        }

    def get_daemon_instances(self) -> Dict[str, DaemonInstanceArgs]:
        return {}

    def get_anvil_instance(self, **kwargs) -> LaunchAnvilInstanceArgs:
        if not "balance" in kwargs:
            kwargs["balance"] = 1000
        if not "accounts" in kwargs:
            kwargs["accounts"] = 2
        if not "fork_url" in kwargs:
            kwargs["fork_url"] = ETH_RPC_URL
        if not "mnemonic" in kwargs:
            kwargs["mnemonic"] = self.mnemonic
        return LaunchAnvilInstanceArgs(
            **kwargs,
        )

    def get_instance_id(self) -> str:
        return f"chal-{CHALLENGE}-{self.team}".lower()

    def update_metadata(self, new_metadata: Dict[str, str]):
        self.metadata[self.team] = new_metadata
        pass

    def deploy_challenge(self) -> int:
        print("deploying challenge...")
        challenge_addr = self.deploy(self.mnemonic)

        self.update_metadata(
            {"mnemonic": self.mnemonic, "challenge_address": challenge_addr}
        )

        print()
        print(f"your challenge has been deployed")
        print(f"---")
        print(f"rpc endpoints:")
        print("TODO")
        print(f"private key:        {get_player_account(self.mnemonic).key.hex()}")
        print(f"challenge contract: {challenge_addr}")
        return 0

    def deploy(self, mnemonic: str) -> str:
        web3 = get_web3()

        return deploy(
            web3,
            self.project_location,
            mnemonic,
        )
