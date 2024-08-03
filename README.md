# Helloweb3

Helloweb3 is a framework for writing blockchain CTF challenges.
It is build as a versioned python package to minimize copy-pasting,
and the architecture is modular.
Out of the box, a mixin for Solidity challenges running on an isolated [Anvil] instance,
as well as support for a simple PoW rate-limiting scheme are provided.

See the examples or template to get started.

## Tricks
You can use this command to launch a web-based blockchain explorer on your challenge:
```sh
docker run -p 8000:80 -e ERIGON_URL=$rpc_url otterscan/otterscan
```
Then, navigate to https://localhost:8000

The template also includes glue code to solve using a [Forge] script.

[Anvil]: https://book.getfoundry.sh/anvil/
[Forge]: https://book.getfoundry.sh/forge/
