import os

from eth_abi import abi

from ctf_launchers.launcher import Action, Launcher
from ctf_launchers.team_provider import TeamProvider, get_team_provider

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
        self.token = self.metadata[self.team]["token"]

        if not self.is_solved(addr):
            print("are you sure you solved it?")
            return 1

        print(FLAG)
        return 0

    def is_solved(self, addr: str) -> bool:
        (result,) = abi.decode(
            ["bool"],
            self.web3.eth.call(
                {
                    "to": addr,
                    "data": self.web3.keccak(text="isSolved()")[:4],
                }
            ),
        )
        return result
