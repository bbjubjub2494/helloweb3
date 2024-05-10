import os

from eth_abi import abi

from .actions import Action
from .anvil import ChallengeWithAnvil

FLAG = os.getenv("FLAG", "EPFL{flag}")


class PwnChallengeWithAnvil(ChallengeWithAnvil):
    @classmethod
    def actions(cls):
        actions = super().actions()
        actions.append(Action("get flag", cls._get_flag))
        return actions

    @classmethod
    async def _get_flag(cls, conn):
        token = await cls._request_token(conn)
        chal = cls.instances[token]
        await chal.get_flag(conn)

    @classmethod
    async def _request_token(cls, conn):
        token = await conn.input("token? ")
        if not token.isalnum():
            await conn.print("bad token")
            raise Exception("bad token")
        if token not in cls.instances:
            await conn.print("instance not found")
            raise Exception("instance not found")
        return token

    async def get_flag(self, conn):
        if await self.is_solved():
            await conn.print(FLAG)
        else:
            await conn.print("are you sure you solved it?")

    async def is_solved(self) -> bool:
        (result,) = abi.decode(
            ["bool"],
            await self.async_web3.eth.call(
                {
                    "to": self.challenge_addr,
                    "data": self.web3.keccak(text="isSolved()")[:4],
                }
            ),
        )
        return bool(result)
