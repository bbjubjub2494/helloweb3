from pwn import *

import os, json, time, string

from eth_account import Account
from web3 import Web3, HTTPProvider
from web3.middleware import construct_sign_and_send_raw_middleware
from web3.exceptions import ContractPanicError

r = remote('localhost', 1337)

r.recvuntil(b'action? ')
r.sendline(b'1')

r.recvuntil("prefix:")
prefix = r.recvline().strip().decode()
r.recvuntil("difficulty:")
difficulty = int(r.recvline().strip().decode())
TARGET = 2**(256-difficulty)
alphabet = string.ascii_letters+string.digits+'+/'
answer = iters.bruteforce(lambda x: int.from_bytes(util.hashes.sha256sum((prefix + x).encode()), 'big') < TARGET, alphabet, length=7)
r.sendlineafter(b">", answer)

r.recvuntil(b'token:')
token = r.recvline().strip()
r.recvuntil(b'rpc endpoint:')
rpc_url = r.recvline().strip().decode()
r.recvuntil(b'private key:')
privk = r.recvline().strip().decode()
r.recvuntil(b'challenge contract:')
challenge_addr = r.recvline().strip().decode()

CHALLENGE_ABI = json.load(open("contracts/out/Challenge.sol/Challenge.json"))['abi']


acct = Account.from_key(privk)
web3 = Web3(HTTPProvider(rpc_url))
web3.middleware_onion.add(construct_sign_and_send_raw_middleware(acct))
web3.eth.default_account = acct.address

challenge = web3.eth.contract(address=challenge_addr, abi=CHALLENGE_ABI)

tx_hash = challenge.functions._win().transact()
tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
assert tx_receipt['status']

assert challenge.functions.isSolved().call()

r = remote('localhost', 1337)

r.recvuntil(b'action? ')
r.sendline(b'2')
r.recvuntil(b'token? ')
r.sendline(token)
r.interactive()
