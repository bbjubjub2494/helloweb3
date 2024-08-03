import abc

from .actions import Action, handle_with_actions


class ChallengeBase(abc.ABC):
    """
    Base class for interactive CTF challenges.
    """
    @classmethod
    @abc.abstractmethod
    def actions(cls) -> list[Action]:
        pass
