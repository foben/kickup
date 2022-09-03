from abc import ABC, abstractmethod
from typing import List

from kickup.domain.entities import MatchResultDouble, Player, PickupMatch


class MatchResultRepository(ABC):

    @abstractmethod
    def all_double_results(self) -> List[MatchResultDouble]:
        raise NotImplementedError

    @abstractmethod
    def save_double_result(self, match_result: MatchResultDouble):
        raise NotImplementedError


class PlayerRepository(ABC):

    @abstractmethod
    def by_id(self, player_id) -> Player:
        raise NotImplementedError

    @abstractmethod
    def create_update(self, player: Player):
        raise NotImplementedError

    @abstractmethod
    def by_external_id(self, external_id_type, external_id) -> Player:
        raise NotImplementedError


class PickupMatchRepository(ABC):

    @abstractmethod
    def by_id(self, match_id) -> PickupMatch:
        raise NotImplementedError

    @abstractmethod
    def create_update(self, match: PickupMatch):
        raise NotImplementedError
