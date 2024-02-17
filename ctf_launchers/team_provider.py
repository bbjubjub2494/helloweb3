import abc
import os
from hashlib import md5
from typing import Optional

import requests


class TeamProvider(abc.ABC):
    @abc.abstractmethod
    def get_team(self) -> Optional[str]:
        pass


class LocalTeamProvider(TeamProvider):
    def __init__(self, team_id):
        self.__team_id = team_id

    def get_team(self):
        return self.__team_id


class RemoteTeamProvider(TeamProvider):
    def get_team(self):
        team_id = self.__check(input("team token? "))
        if not team_id:
            print("invalid team token!")
            return None

        return team_id

    def __check(self, token: str) -> str:
        # TODO: pow or something
        return md5(token.encode()).hexdigest()



def get_team_provider() -> TeamProvider:
    # TODO: pow or something
    if False:
        return RemoteTeamProvider(rw_api_token)
    else:
        return LocalTeamProvider(team_id="local")

