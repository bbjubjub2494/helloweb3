import hashlib
import secrets

from .util import TextStreamRequestHandler


# copied from: https://github.com/balsn/proof-of-work
class NcPowser:
    def __init__(self, difficulty=22, prefix_length=16):
        self.difficulty = difficulty
        self.prefix_length = prefix_length

    def get_challenge(self):
        return secrets.token_urlsafe(self.prefix_length)[:self.prefix_length].replace('-', 'b').replace('_', 'a')

    def verify_hash(self, prefix, answer):
        h = hashlib.sha256()
        h.update((prefix + answer).encode())
        bits = ''.join(bin(i)[2:].zfill(8) for i in h.digest())
        return bits.startswith('0' * self.difficulty)

class Pow(TextStreamRequestHandler):
    async def require_pow(self):
        powser = NcPowser()
        prefix = powser.get_challenge()
        self.print(f"please : sha256({prefix} + ???) == {'0'*powser.difficulty}({powser.difficulty})... ")
        self.print(f"prefix: {prefix}")
        self.print(f"difficulty: {powser.difficulty}")
        answer = self.input(" >")
        if not powser.verify_hash(prefix, answer):
            self.print("no etherbase for you")
            raise Exception("invalid pow")
