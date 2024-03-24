import os
import subprocess

from eth_account import Account
from eth_account.account import LocalAccount
from eth_account.hdaccount import key_from_seed, seed_from_mnemonic
from web3.types import RPCResponse


DEFAULT_DERIVATION_PATH = "m/44'/60'/0'/0/"

def get_account(mnemonic: str, offset: int) -> LocalAccount:
    seed = seed_from_mnemonic(mnemonic, "")
    private_key = key_from_seed(seed, f"{DEFAULT_DERIVATION_PATH}{offset}")

    return Account.from_key(private_key)


def get_player_account(mnemonic: str) -> LocalAccount:
    return get_account(mnemonic, 0)


def get_additional_account(mnemonic: str, offset: int) -> LocalAccount:
    return get_account(mnemonic, offset + 2)

def deploy(
    web3,
    token,
    project_location: str,
    mnemonic: str,
    deploy_script: str = "script/Deploy.s.sol:Deploy",
    env: dict = {},
) -> str:
    rfd, wfd = os.pipe2(os.O_NONBLOCK)

    proc = subprocess.Popen(
        args=[
            "/opt/foundry/bin/forge",
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
            "PATH": "/opt/foundry/bin:/usr/bin:" + os.getenv("PATH", "/fake"),
            "MNEMONIC": mnemonic,
            "OUTPUT_FILE": f"/proc/self/fd/{wfd}",
        }
        | env,
        pass_fds=[wfd],
        cwd=project_location,
        text=True,
        encoding="utf8",
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    stdout, stderr = proc.communicate()

    if proc.returncode != 0:
        print(stdout)
        print(stderr)
        raise Exception("forge failed to run")

    result = os.read(rfd, 256).decode("utf8")

    os.close(rfd)
    os.close(wfd)

    return result


def check_error(resp: RPCResponse):
    if "error" in resp:
        raise Exception("rpc exception", resp["error"])
