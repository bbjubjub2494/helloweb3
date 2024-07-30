# Helloweb3

## Tricks
You can use this command to launch a web-based blockchain explorer on your challenge:
```sh
docker run -p 8000:80 -e ERIGON_URL=$rpc_url otterscan/otterscan
```

Then, navigate to https://localhost:8000
