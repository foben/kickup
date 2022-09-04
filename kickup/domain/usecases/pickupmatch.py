import logging
import random

from kickup.domain.entities import (
    PickupMatch,
    Player,
    PickupMatchStatus,
    MatchResultDouble,
)
from kickup.domain.repositories import PickupMatchRepository, MatchResultRepository

WINNING_SCORE = 6


class PickupMatchUsecase:
    def __init__(
        self,
        pickup_match_repo: PickupMatchRepository,
        match_repo: MatchResultRepository,
    ):
        if not isinstance(pickup_match_repo, PickupMatchRepository):
            raise TypeError("Not a proper PickupMatchRepository")
        if not isinstance(match_repo, MatchResultRepository):
            raise TypeError("Not a proper MatchResultRepository")
        self.pickup_match_repo = pickup_match_repo
        self.match_repo = match_repo

    def create_pickup_match(self) -> PickupMatch:
        p = PickupMatch()
        self.pickup_match_repo.create_update(p)
        return p

    def cancel_pickup_match(self, pickup_match: PickupMatch) -> PickupMatch:
        pickup_match.status = PickupMatchStatus.CANCELED
        self.pickup_match_repo.create_update(pickup_match)
        return pickup_match

    def join_pickup_match(
        self, pickup_match: PickupMatch, player: Player
    ) -> PickupMatch:
        if pickup_match.status != PickupMatchStatus.OPEN:
            raise NotImplementedError  # TODO
        logging.info(f"player {player} has joined pickup match {pickup_match}")
        pickup_match.candidates.add(player)
        self.pickup_match_repo.create_update(pickup_match)
        return pickup_match

    def leave_pickup_match(
        self, pickup_match: PickupMatch, player: Player
    ) -> PickupMatch:
        if pickup_match.status != PickupMatchStatus.OPEN:
            raise NotImplementedError  # TODO
        if player in pickup_match.candidates:
            pickup_match.candidates.remove(player)
        self.pickup_match_repo.create_update(pickup_match)
        return pickup_match

    def start_pickup_match(self, pickup_match: PickupMatch) -> PickupMatch:
        if len(pickup_match.candidates) < 4:
            raise ValueError("Too few players to start")
        if pickup_match.status != PickupMatchStatus.OPEN:
            raise ValueError(f"Cannot start a match in status {pickup_match.status}")

        players = random.sample(pickup_match.candidates, 4)
        pickup_match.a_goalie = players[0]
        pickup_match.a_striker = players[1]
        pickup_match.b_goalie = players[2]
        pickup_match.b_striker = players[3]

        pickup_match.status = PickupMatchStatus.STARTED
        self.pickup_match_repo.create_update(pickup_match)
        return pickup_match

    def set_team_a_score(self, pickup_match: PickupMatch, score: int) -> PickupMatch:
        if score < 0 or score > WINNING_SCORE:
            raise ValueError(f"{score} is an invalid score")
        pickup_match.a_score = score
        self.pickup_match_repo.create_update(pickup_match)
        return pickup_match

    def set_team_b_score(self, pickup_match: PickupMatch, score: int) -> PickupMatch:
        if score < 0 or score > WINNING_SCORE:
            raise ValueError(f"{score} is an invalid score")
        pickup_match.b_score = score
        self.pickup_match_repo.create_update(pickup_match)
        return pickup_match

    def resolve_match(self, pickup_match: PickupMatch) -> PickupMatch:
        if pickup_match.status == PickupMatchStatus.RESOLVED:
            logging.warning(f"match {pickup_match.id} was resolved before!")
            return pickup_match
        if pickup_match.status == PickupMatchStatus.OPEN:
            logging.warning(f"match { pickup_match.id } has not even started!")
            return pickup_match
        if pickup_match.status == PickupMatchStatus.CANCELED:
            logging.warning(f"match { pickup_match.id } was cancelled")
            return pickup_match

        if pickup_match.a_score != 6 and pickup_match.b_score != 6:
            logging.warning("At least one team needs 6 goals!")
            return pickup_match
        if pickup_match.a_score == 6 and pickup_match.b_score == 6:
            logging.warning("Both teams can't have score 6!")
            return pickup_match

        pickup_match.status = PickupMatchStatus.RESOLVED

        res = MatchResultDouble(
            pickup_match.a_goalie,
            pickup_match.a_striker,
            pickup_match.b_goalie,
            pickup_match.b_striker,
            pickup_match.a_score,
            pickup_match.b_score,
        )
        self.pickup_match_repo.create_update(pickup_match)
        self.match_repo.save_double_result(res)
        return pickup_match
