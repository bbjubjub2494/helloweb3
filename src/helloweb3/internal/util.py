import os
import subprocess

from eth_account import Account
Account.enable_unaudited_hdwallet_features()


class PlayerError(Exception):
    """
    Raised when a player provides invalid input.
    It should result in terminating the connection.
    """


def _get_account(mnemonic, n):
    # pylint: disable=no-value-for-parameter
    return Account.from_mnemonic(mnemonic,account_path=f"m/44'/60'/0'/0/{n}")

def get_player_account(mnemonic):
    return _get_account(mnemonic, 1)

def deploy(
    web3,
    token,
    project_location: str,
    mnemonic: str,
    deploy_script: str = "script/Deploy.s.sol:Deploy",
) -> str:
    rfd, wfd = os.pipe2(os.O_NONBLOCK)

    proc = subprocess.run(
        args=[
            "forge",
            "script",
            "--rpc-url",
            f"http://127.0.0.1:8545/{token}",
            "--broadcast",
            "--unlocked",
            "--sender",
            web3.eth.accounts[0],
            deploy_script,
        ],
        env={
            "MNEMONIC": mnemonic,
            "OUTPUT_FILE": f"/proc/self/fd/{wfd}",
        }
        | os.environ,
        pass_fds=[wfd],
        cwd=project_location,
        check=True,
    )

    if proc.returncode != 0:
        raise PlayerError("forge failed to run")

    result = os.read(rfd, 256).decode("utf8")

    os.close(rfd)
    os.close(wfd)

    return result
