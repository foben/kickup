import logging
import random

from kickup.domain.entities import PickupMatch, Player, PickupMatchStatus, MatchResultDouble
from kickup.domain.repositories import PickupMatchRepository, PlayerRepository, MatchResultRepository

WINNING_SCORE = 6


class PickupMatchUsecase:

    def __init__(self, pickup_match_repo: PickupMatchRepository, player_repo: PlayerRepository, match_repo: MatchResultRepository):
        if not isinstance(pickup_match_repo, PickupMatchRepository):
            raise TypeError('Not a proper PickupMatchRepository')
        if not isinstance(player_repo, PlayerRepository):
            raise TypeError('Not a proper PickupMatchRepository')
        if not isinstance(match_repo, MatchResultRepository):
            raise TypeError('Not a proper MatchResultRepository')
        self.pickup_match_repo = pickup_match_repo
        self.player_repo = player_repo
        self.match_repo = match_repo

    def create_pickup_match(self) -> PickupMatch:
        p = PickupMatch()
        self.pickup_match_repo.create_update(p)
        return p

    def cancel_pickup_match(self, pickup_match_id: str) -> PickupMatch:
        p = self.pickup_match_repo.by_id(pickup_match_id)
        if not p:
            raise NotImplementedError  # TODO
        p.status = PickupMatchStatus.CANCELED
        self.pickup_match_repo.create_update(p)
        return p

    def join_pickup_match(self, pickup_match_id: str, player_id: str) -> PickupMatch:
        p = self.pickup_match_repo.by_id(pickup_match_id)
        player = self.player_repo.by_id(player_id)
        if not p or not player:
            raise NotImplementedError  # TODO
        if p.status != PickupMatchStatus.OPEN:
            raise NotImplementedError  # TODO
        logging.info(f"player {player} has joined pickup match {p}")
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

    def resolve_match(self, pickup_match_id: str) -> PickupMatch:
        p = self.pickup_match_repo.by_id(pickup_match_id)
        if not p:
            raise ValueError(f"match not found: {pickup_match_id}")
        if p.status == PickupMatchStatus.RESOLVED:
            logging.warning(f'match {pickup_match_id} was resolved before!')
            return p
        if p.status == PickupMatchStatus.OPEN:
            logging.warning(f'match { pickup_match_id } has not even started!')
            return p
        if p.status == PickupMatchStatus.CANCELED:
            logging.warning(f'match { pickup_match_id } was cancelled')
            return p

        if p.a_score != 6 and p.b_score != 6:
            logging.warning('At least one team needs 6 goals!')
            return p
        if p.a_score == 6 and p.b_score == 6:
            logging.warning('Both teams can\'t have score 6!')
            return p

        p.status = PickupMatchStatus.RESOLVED

        res = MatchResultDouble(
            p.a_goalie, p.a_striker, p.b_goalie, p.b_striker, p.a_score, p.b_score
        )
        self.pickup_match_repo.create_update(p)
        self.match_repo.save_double_result(res)
        return p



