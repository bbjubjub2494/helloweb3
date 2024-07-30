import io
import os
import subprocess
import socketserver

from eth_account import Account
Account.enable_unaudited_hdwallet_features()

def _get_account(mnemonic, n):
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

    proc = subprocess.Popen(
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
        text=True,
        encoding="utf8",
        stdin=subprocess.DEVNULL,
    )
    stdout, stderr = proc.communicate()

    if proc.returncode != 0:
        raise Exception("forge failed to run")

    result = os.read(rfd, 256).decode("utf8")

    os.close(rfd)
    os.close(wfd)

    return result
