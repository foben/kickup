import random
import logging
import datetime
import copy
from dataclasses import dataclass

from kickup.domain.entities import PickupMatch, PickupMatchStatus, Player as DomainPlayer
from kickup.persistence import persistence
from kickup.persistence.persistence import Player

KICKUPS = {}

@dataclass
class Pairing:
    goal_A: persistence.Player
    strike_A: persistence.Player

    goal_B: persistence.Player
    strike_B: persistence.Player

OPEN = 'open'
RUNNING = 'running'
RESOLVED = 'resolved'
CANCELLED = 'cancelled'


# def new_kickup():
#     while True:
#         num = random.randint(10000, 1000000)
#         if num not in KICKUPS: break
#     KICKUPS[num] = KickUp(num)
#     return KICKUPS[num]
#
# def get_kickup(num):
#     if not num in KICKUPS:
#         return None
#     return KICKUPS[num]


# This should be the slack 'DTO' for pickup matches
class KickUp:

    def __init__(self, num):
        self.num = num
        self.state = OPEN
        self.players = set()
        self.pairing = None
        self.warnings = set()
        self.score_B = 0
        self.score_A = 0

    # def add_player(self, player):
    #     if player in self.players:
    #         logging.info(f'Already in kickup {self.num}: { player }')
    #         return False
    #     else:
    #         logging.info(f'Player joined kickup {self.num}: { player }')
    #         self.players.add(player)
    #         return True
    #
    # def start_match(self):
    #     if len(self.players) < 4:
    #         self.warnings.add('Need at least 4 players to start!')
    #         return
    #     if self.state == RUNNING:
    #         logging.info('already started')
    #         return
    #     logging.info(f'Kickup Match { self.num } has been started')
    #     self.pairing = Pairing(*random.sample(self.players, 4))
    #     self.state = RUNNING
    #     self.possible_scores()
    #
    # def possible_scores(self):
    #     match_win_A = persistence.Match(
    #         self.pairing.goal_A._id,
    #         self.pairing.strike_A._id,
    #         self.pairing.goal_B._id,
    #         self.pairing.strike_B._id,
    #         6, 0,
    #         datetime.datetime.now(),
    #     )
    #     match_win_B = copy.deepcopy(match_win_A)
    #     match_win_B.score_A = 0
    #     match_win_B.score_B = 6
    #     self.max_win_A = elo.leaderboard(persistence.matches_sorted()).eval_match(match_win_A).last_delta
    #     self.max_win_B = elo.leaderboard(persistence.matches_sorted()).eval_match(match_win_B).last_delta
    #
    # def resolve_match(self):
    #     if self.state == RESOLVED:
    #         logging.warning(f'Kickup { self.num } was resolved before!')
    #         return False
    #     if self.state == OPEN:
    #         logging.warning(f'Kickup { self.num } has not even started!')
    #         return False
    #     if self.score_B != 6 and self.score_A != 6:
    #         self.warnings.add('At least one team needs 6 goals!')
    #         return False
    #     if self.score_B == 6 and self.score_A == 6:
    #         self.warnings.add('Both teams can\'t have score 6!')
    #         return False
    #     logging.info(f'Kickup { self.num } has been resolved A { self.score_A }:{ self.score_B } B')
    #     #TODO: this gives exactly one chance to save to db
    #     self.state = RESOLVED
    #     return True
    #
    def process_warnings(self):
        if not self.warnings:
            return None
        result = self.warnings.copy()
        self.warnings = set()
        return result
    #
    # def cancel(self):
    #     self.state = CANCELLED


def map_domain_state(domain_state: PickupMatchStatus) -> str:
    if domain_state == PickupMatchStatus.OPEN:
        return OPEN
    elif domain_state == PickupMatchStatus.STARTED:
        return RUNNING
    elif domain_state == PickupMatchStatus.RESOLVED:
        return RESOLVED
    elif domain_state == PickupMatchStatus.CANCELED:
        return CANCELLED
    else:
        raise ValueError(f"couldn't map domain state {domain_state}")


def map_domain_player(domain_player: DomainPlayer) -> Player:
    return Player(
        domain_player.name,
        "unmappable",
        domain_player.id
    )


def map_domain_pickup_match_pairing(pickup_match: PickupMatch) -> Pairing:
    # if one field's missing, there shouldn't be any other position fields set
    if pickup_match.a_goalie is None:
        return None
    return Pairing(
        map_domain_player(pickup_match.a_goalie),
        map_domain_player(pickup_match.a_striker),
        map_domain_player(pickup_match.b_goalie),
        map_domain_player(pickup_match.b_striker),
    )


def map_domain_pickup_match_to_slack_dto(pickup_match: PickupMatch) -> KickUp:
    k = KickUp(
        pickup_match.id
    )
    k.state = map_domain_state(pickup_match.status)
    k.players = set(pickup_match.candidates)

    k.pairing = map_domain_pickup_match_pairing(pickup_match)
    k.warnings = {"warnings not mappable"}
    k.score_A = pickup_match.a_score
    k.score_B = pickup_match.b_score
    return k
