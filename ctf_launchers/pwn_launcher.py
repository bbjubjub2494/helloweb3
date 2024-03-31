import os

from eth_abi import abi

from ctf_launchers.launcher import Action, Launcher

FLAG = os.getenv("FLAG", "EPFL{flag}")


class PwnChallengeLauncher(Launcher):
    def __init__(
        self, request, client_address, server,
        project_location: str = "challenge/contracts",
    ):
        super().__init__(request, client_address, server,
            project_location,
            [
                Action(name="get flag", handler=self.get_flag),
            ],
        )

    def get_flag(self) -> int:
        self.request_token()
        addr = self.metadata[self.token]["challenge_address"]

        if not self.is_solved(addr):
            self.print("are you sure you solved it?")
            return

        self.print(FLAG)

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
