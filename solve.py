from pwn import *

import os, json, time, string

from eth_account import Account

r = remote("localhost", 1337)

r.recvuntil(b"action? ")
r.sendline(b"1")

r.recvuntil("prefix:")
prefix = r.recvline().strip().decode()
r.recvuntil("difficulty:")
difficulty = int(r.recvline().strip().decode())
TARGET = 2 ** (256 - difficulty)
alphabet = string.ascii_letters + string.digits + "+/"
answer = iters.bruteforce(
    lambda x: int.from_bytes(util.hashes.sha256sum((prefix + x).encode()), "big")
    < TARGET,
    alphabet,
    length=7,
)
r.sendlineafter(b">", answer)

r.recvuntil(b"token:")
token = r.recvline().strip()
r.recvuntil(b"rpc endpoint:")
rpc_url = r.recvline().strip().decode()
r.recvuntil(b"private key:")
privk = r.recvline().strip().decode()
r.recvuntil(b"challenge contract:")
challenge_addr = r.recvline().strip().decode()

CHALLENGE_ABI = json.load(open("contracts/out/Challenge.sol/Challenge.json"))["abi"]
print(rpc_url)
