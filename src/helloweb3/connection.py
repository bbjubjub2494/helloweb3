import io


class Connection:
    """
    A connection opened by a CTF player.
    """
    def __init__(self, reader, writer):
        self._reader = reader
        self._writer = writer

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

    def close(self):
        self._writer.close()

    def __enter__(self):
        return self

    def __exit__(self, *exc_details):
        self._writer.close()
        return False
