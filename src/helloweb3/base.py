import abc

from .actions import Action


class ChallengeBase(abc.ABC):
    """
    Base class for interactive CTF challenges.
    """
    @classmethod
    @abc.abstractmethod
    def actions(cls) -> list[Action]:
        return []
