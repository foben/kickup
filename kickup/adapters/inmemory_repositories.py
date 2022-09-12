from typing import List

from kickup.domain.entities import MatchResultDouble, PickupMatch, Player
from kickup.domain.repositories import (
    MatchResultRepository,
    PickupMatchRepository,
    PlayerRepository,
)


class InMemoryMatchResultRepository(MatchResultRepository):
    def __init__(self):
        self.matches = {}

    def all_double_results(self) -> List[MatchResultDouble]:
        return list(self.matches.values())

    def save_double_result(self, match_result: MatchResultDouble):
        self.matches[match_result.id] = match_result

    def games_by_player(self, player: Player) -> List[MatchResultDouble]:
        raise NotImplementedError


class InMemoryPickupMatchRepository(PickupMatchRepository):
    def __init__(self):
        self.pickup_matches = {}

    def get_all(self) -> List[PickupMatch]:
        return list(self.pickup_matches.values())

    def by_id(self, match_id) -> PickupMatch:
        if match_id in self.pickup_matches:
            return self.pickup_matches[match_id]
        else:
            raise ValueError(f"Id not found: {match_id}")

    def create_update(self, match: PickupMatch):
        if match.id is None or match.id == "":
            raise ValueError("No id set")
        self.pickup_matches[match.id] = match


class InMemoryPlayerRepository(PlayerRepository):
    def __init__(self):
        self.players = {}

    def by_id(self, player_id) -> Player:
        if player_id in self.players:
            return self.players[player_id]
        else:
            raise ValueError(f"Id not found: {player_id}")

    def create_update(self, player: Player):
        if player.id is None or player.id == "":
            raise ValueError("No id set")
        self.players[player.id] = player

    def by_external_id(self, external_id_type, external_id) -> Player:
        raise NotImplementedError("TODO!")
