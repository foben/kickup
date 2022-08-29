import random

from kickup.domain.entities import PickupMatch, Player, PickupMatchStatus
from kickup.domain.repositories import PickupMatchRepository, PlayerRepository

WINNING_SCORE = 6

class PickupMatchUsecase:

    def __init__(self, pickup_match_repo: PickupMatchRepository, player_repo: PlayerRepository):
        if not isinstance(pickup_match_repo, PickupMatchRepository):
            raise TypeError('Not a proper PickupMatchRepository')
        if not isinstance(player_repo, PlayerRepository):
            raise TypeError('Not a proper PickupMatchRepository')
        self.pickup_match_repo = pickup_match_repo
        self.player_repo = player_repo

    def create_pickup_match(self) -> PickupMatch:
        p = PickupMatch()
        self.pickup_match_repo.create_update(p)
        return p

    def join_pickup_match(self, pickup_match_id: str, player_id: str) -> PickupMatch:
        p = self.pickup_match_repo.by_id(pickup_match_id)
        player = self.player_repo.by_id(player_id)
        if not p or not player:
            raise NotImplementedError # TODO
        if p.status != PickupMatchStatus.OPEN:
            raise NotImplementedError  # TODO
        p.candidates.add(player)
        self.pickup_match_repo.create_update(p)
        return p

    def leave_pickup_match(self, pickup_match_id: str, player_id: str) -> PickupMatch:
        p = self.pickup_match_repo.by_id(pickup_match_id)
        player = self.player_repo.by_id(player_id)
        if p.status != PickupMatchStatus.OPEN:
            raise NotImplementedError  # TODO
        if player in p.candidates:
            p.candidates.remove(player)
        self.pickup_match_repo.create_update(p)
        return p

    def start_pickup_match(self, pickup_match_id: str) -> PickupMatch:
        p = self.pickup_match_repo.by_id(pickup_match_id)
        if len(p.candidates) < 4:
            raise ValueError("Too few players to start")
        if p.status != PickupMatchStatus.OPEN:
            raise ValueError(f"Cannot start a match in status {p.status}")

        players = random.sample(p.candidates, 4)
        p.a_goalie = players[0]
        p.a_striker = players[1]
        p.b_goalie = players[2]
        p.b_striker = players[3]

        p.status = PickupMatchStatus.STARTED
        self.pickup_match_repo.create_update(p)
        return p

    def set_team_a_score(self, pickup_match_id: str, score: int) -> PickupMatch:
        if score < 0 or score > WINNING_SCORE:
            raise ValueError(f"{score} is an invalid score")
        p = self.pickup_match_repo.by_id(pickup_match_id)
        p.a_score = score
        self.pickup_match_repo.create_update(p)
        return p

    def set_team_b_score(self, pickup_match_id: str, score: int) -> PickupMatch:
        if score < 0 or score > WINNING_SCORE:
            raise ValueError(f"{score} is an invalid score")
        p = self.pickup_match_repo.by_id(pickup_match_id)
        p.b_score = score
        self.pickup_match_repo.create_update(p)
        return p


