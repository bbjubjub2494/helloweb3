import hashlib
import os
import secrets

from .anvil import ChallengeWithAnvil
from .internal.util import PlayerError


POW_DIFFICULTY = int(os.getenv("POW_DIFFICULTY", "0"))

# copied from: https://github.com/balsn/proof-of-work
class NcPowser:
    def __init__(self, difficulty=22, prefix_length=16):
        self.difficulty = difficulty
        self.prefix_length = prefix_length

    def get_challenge(self):
        return (
            secrets.token_urlsafe(self.prefix_length)[: self.prefix_length]
            .replace("-", "b")
            .replace("_", "a")
        )

    def verify_hash(self, prefix, answer):
        h = hashlib.sha256()
        h.update((prefix + answer).encode())
        bits = "".join(bin(i)[2:].zfill(8) for i in h.digest())
        return bits.startswith("0" * self.difficulty)


class ChallengeWithAnvilAndPow(ChallengeWithAnvil):
    """
    A challenge which will impose a proof-of-work puzzle on each deployment.
    """
    async def _require_pow(self, conn):
        powser = NcPowser(POW_DIFFICULTY)
        prefix = powser.get_challenge()
        await conn.print(
            f"please : sha256({prefix} + ???) == {'0'*powser.difficulty}({powser.difficulty})... "
        )
        await conn.print(f"prefix: {prefix}")
        await conn.print(f"difficulty: {powser.difficulty}")
        answer = await conn.input(" >")
        if not powser.verify_hash(prefix, answer):
            raise PlayerError("invalid pow")

    async def deploy(self, conn):
        await self._require_pow(conn)
        await super().deploy(conn)
