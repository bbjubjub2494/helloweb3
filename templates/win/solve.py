from pwn import *

import string, subprocess

r = remote(args.get('HOST', "localhost"), args.get('PORT', 1337))

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

rpc_url = rpc_url.replace("127.0.0.1", args['HOST'])
subprocess.run([
    "forge", "script",
    "-f", rpc_url,
    "--private-key", privk,
    "--broadcast",
    "Solve",
    "--sig", "run(address challenge)",
    challenge_addr,
],
    cwd="contracts",
)

r = remote(args.get('HOST', "localhost"), args.get('PORT', 1337))
r.recvuntil(b"action? ")
r.sendline(b"2")
r.recvuntil(b"token? ")
r.sendline(token)
r.interactive()
