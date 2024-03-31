import socketserver

from ctf_launchers.pwn_launcher import PwnChallengeLauncher


class Challenge(PwnChallengeLauncher):
    pass


with socketserver.ThreadingTCPServer(('0.0.0.0', 1337), Challenge) as server:
    server.serve_forever()
