import os

from eth_abi import abi

from ctf_launchers.launcher import Action, Launcher
from ctf_launchers.team_provider import TeamProvider, get_team_provider
from ctf_launchers.utils import deploy, get_web3

FLAG = os.getenv("FLAG", "EPFL{flag}")


class PwnChallengeLauncher(Launcher):
    def __init__(
        self,
        project_location: str = "challenge/contracts",
        provider: TeamProvider = get_team_provider(),
    ):
        super().__init__(
            project_location,
            provider,
            [
                Action(name="get flag", handler=self.get_flag),
            ],
        )

    def get_flag(self) -> int:
        addr = self.metadata[self.team]["challenge_address"]
        if not self.is_solved(addr):
            print("are you sure you solved it?")
            return 1

        print(FLAG)
        return 0

    def is_solved(self, addr: str) -> bool:
        web3 = get_web3(self.metadata[self.team]["token"])

        (result,) = abi.decode(
            ["bool"],
            web3.eth.call(
                {
                    "to": addr,
                    "data": web3.keccak(text="isSolved()")[:4],
                }
            ),
        )
        return result
