from typing import Dict

from eth_abi import abi

from ctf_launchers.pwn_launcher import PwnChallengeLauncher
from ctf_launchers.types import (DaemonInstanceArgs, LaunchAnvilInstanceArgs,
                                 UserData, get_additional_account,
                                 )


class Challenge(PwnChallengeLauncher):
    pass

Challenge().run()
