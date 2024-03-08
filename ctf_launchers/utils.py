import json
import os
import subprocess
from typing import Dict

from web3 import Web3
from web3.types import RPCResponse


def deploy(
    web3: Web3,
    token,
    project_location: str,
    mnemonic: str,
    deploy_script: str = "script/Deploy.s.sol:Deploy",
    env: Dict = {},
) -> str:
    rfd, wfd = os.pipe2(os.O_NONBLOCK)

    proc = subprocess.Popen(
        args=[
            "/opt/foundry/bin/forge",
            "script",
            "--rpc-url",
            f"http://127.0.0.1:1338/{token}",
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

def get_web3(token):
    return Web3(Web3.IPCProvider(os.path.join("/tmp/geths", token, "geth.ipc")))
