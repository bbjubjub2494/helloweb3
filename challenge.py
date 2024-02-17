from typing import Dict

from eth_abi import abi

from ctf_launchers.pwn_launcher import PwnChallengeLauncher
from ctf_launchers.types import (DaemonInstanceArgs, LaunchAnvilInstanceArgs,
                                 UserData, get_additional_account,
                                 get_privileged_web3)
from ctf_launchers.utils import (anvil_setCodeFromFile, anvil_setStorageAt,
                                 deploy)


class Challenge(PwnChallengeLauncher):
    pass
