# Helloweb3

Helloweb3 is a framework for writing blockchain CTF challenges.
It is build as a versioned python package to minimize copy-pasting,
and the architecture is modular.
Out of the box, a mixin for Solidity challenges running on an isolated [Anvil] instance,
as well as support for a simple PoW rate-limiting scheme are provided.

See the templates to get started.

## Caveats

Foundry now ships two ways to fetch dependencies: git submodules and [Soldeer].
Usually, challenge files distributed to players do not come in the form of a git repository.
Thus, Helloweb3 supports Soldeer and we highly recommend using it for challenges.

[Soldeer]: https://book.getfoundry.sh/projects/soldeer

The PyPI package `helloweb3` is under my (`bbjubjub2494`) unilateral control.
I can push new versions and delete old version at will.
However, I do not intend to abuse this capability.
If that is a concern nonetheless, please consider targeting a software source you control, such a a git repository.
Note that pip supports `git+https` URLs.

## Tricks
You can use this command to launch a web-based blockchain explorer on your challenge:
```sh
docker run -p 8000:80 -e ERIGON_URL=$rpc_url otterscan/otterscan
```
Then, navigate to https://localhost:8000

The template also includes glue code to solve using a [Forge] script.

[Anvil]: https://book.getfoundry.sh/anvil/
[Forge]: https://book.getfoundry.sh/forge/

## Testing

I was not able to set up a nice testing framework due to the nature of the code.
The current practice is to pin the commit under test HELLOWEB3 in `examples/win/docker-compose.yaml` after pushing it.

## Credit

Helloweb3 is based on [`paradigmctf.py`] by samcszun, which has often been copy-pasted in other CTFs as well.

[paradigmctf.py]: https://github.com/paradigmxyz/paradigm-ctf-infrastructure/tree/main/paradigmctf.py
