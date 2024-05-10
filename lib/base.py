import contextlib
import dataclasses
import io
import typing


@dataclasses.dataclass
class Action:
    description: str
    handler: typing.Callable[[], typing.Awaitable[None]]


class ChallengeBase:
    """
    Base class for defining an interactive CTF challenge.
    Subclasses should define `actions` that the player can trigger when connecting to the remote.
    They are instantiated for each connection.
    """

    # per-subclass key value database to store challenge instance information
    metadata: dict[str, typing.Any]
    # unique per-instance
    token: str

    async def put_metadata(self, new_metadata: dict[str, str]):
        self.metadata[self.token] = new_metadata

    async def get_metadata(self):
        return self.metadata[self.token]

    async def del_metadata(self):
        del self.metadata[self.token]

    def __init__(self, reader, writer, metadata):
        self._reader = reader
        self._writer = writer
        self.metadata = metadata

    async def print(self, *args, sep=" ", end="\n", flush=False):
        """Send data to the player, with an interface matching `builtins.print`"""
        buf = io.StringIO()
        print(*args, sep=sep, end=end, file=buf, flush=flush)
        self._writer.write(buf.getvalue().encode())
        await self._writer.drain()

    async def input(self, prompt=""):
        """Prompt data from the player, with an interface matching `builtins.input`"""
        self._writer.write(prompt.encode())
        await self._writer.drain()
        return (await self._reader.readline()).decode().strip()

    def __default_action(self) -> Action:
        return Action("say hello", self.__say_hello)

    def actions(self) -> list[Action]:
        """
        Return a list of actions to offer the player upon connection.
        If there's only one action, the prompt is skipped.
        """
        return []

    async def __say_hello(self) -> None:
        await self.print("hello web3")

    async def __prompt_action(self) -> Action:
        actions = self.actions()
        if len(actions) == 0:
            return self.__default_action()
        elif len(actions) == 1:
            return actions[0]
        for i, a in enumerate(actions):
            await self.print(f"{i+1} - {a.description}")
        while True:
            try:
                choice = int(await self.input("action? "))
            except ValueError:
                continue
            if 1 <= choice <= len(actions):
                return actions[choice - 1]

    async def handle(self) -> None:
        """
        Handle a connection from a player.
        """
        with contextlib.closing(self._writer):
            action = await self.__prompt_action()
            await action.handler()
