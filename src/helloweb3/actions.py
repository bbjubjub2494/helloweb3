import dataclasses
import typing

from .connection import Connection


@dataclasses.dataclass
class Action:
    """
    An action can be triggered remotely by the CTF player.
    """
    description: str
    handler: typing.Callable[[Connection], typing.Awaitable[None]]


async def prompt_action(conn: Connection, actions: list[Action]) -> Action:
    if len(actions) == 0:
        return Action("say hello", lambda conn: conn.print("Hello!"))
    elif len(actions) == 1:
        return actions[0]
    for i, a in enumerate(actions):
        await conn.print(f"{i+1} - {a.description}")
    while True:
        try:
            choice = int(await conn.input("action? "))
        except ValueError:
            continue
        if 1 <= choice <= len(actions):
            return actions[choice - 1]


async def handle_with_actions(conn: Connection, actions: list[Action]) -> None:
    """
    Handle a connection from a player.
    """
    action = await prompt_action(conn, actions)
    await action.handler(conn)
