from abc import ABC, abstractmethod
from typing import List

from kickup.domain.entities import MatchResultDouble, Player


class MatchResultRepository(ABC):

    @abstractmethod
    def all_double_results(self) -> List[MatchResultDouble]:
        raise NotImplementedError

    @abstractmethod
    def save_double_result(self, match_result):
        raise NotImplementedError


class PlayerRepository(ABC):

    @abstractmethod
    def by_id(self, player_id) -> Player:
        raise NotImplementedError

