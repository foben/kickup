import copy
import datetime
import logging
import random
from dataclasses import dataclass
import elo
import persistence
from persistence import Player

KICKUPS = {}


@dataclass
class Pairing:
    goal_a: Player
    strike_a: Player

    goal_b: Player
    strike_b: Player


OPEN = 'open'
RUNNING = 'running'
RESOLVED = 'resolved'
CANCELLED = 'cancelled'


def new_kickup():
    while True:
        num = random.randint(10000, 1000000)
        if num not in KICKUPS:
            break
    KICKUPS[num] = KickUp(num)
    return KICKUPS[num]


def get_kickup(num):
    if num not in KICKUPS:
        return None
    return KICKUPS[num]


class KickUp:

    def __init__(self, num):
        self.num = num
        self.state = OPEN
        self.players = set()
        self.pairing = None
        self.warnings = set()
        self.score_a = 0
        self.score_b = 0
        self.max_win_a = 0
        self.max_win_b = 0

    def add_player(self, player):
        if player in self.players:
            logging.info(f'Already in kickup {self.num}: {player}')
            return False
        else:
            logging.info(f'Player joined kickup {self.num}: {player}')
            self.players.add(player)
            return True

    def start_match(self):
        if len(self.players) < 4:
            self.warnings.add('Need at least 4 players to start!')
            return
        if self.state == RUNNING:
            logging.info('already started')
            return
        logging.info(f'Kickup Match {self.num} has been started')
        self.pairing = Pairing(*random.sample(self.players, 4))
        self.state = RUNNING
        self.possible_scores()

    def possible_scores(self):
        match_win_a = persistence.Match(
            self.pairing.goal_a._id,
            self.pairing.strike_a._id,
            self.pairing.goal_b._id,
            self.pairing.strike_b._id,
            6, 0,
            datetime.datetime.now(),
        )
        match_win_b = copy.deepcopy(match_win_a)
        match_win_b.score_a = 0
        match_win_b.score_b = 6
        self.max_win_a = elo.leaderboard(persistence.matches_sorted()).eval_match(match_win_a).last_delta
        self.max_win_b = elo.leaderboard(persistence.matches_sorted()).eval_match(match_win_b).last_delta

    def resolve_match(self):
        if self.state == RESOLVED:
            logging.warning(f'Kickup {self.num} was resolved before!')
            return False
        if self.score_b != 6 and self.score_a != 6:
            self.warnings.add('At least one team needs 6 goals!')
            return False
        if self.score_b == 6 and self.score_a == 6:
            self.warnings.add('Both teams can\'t have score 6!')
            return False
        logging.info(f'Kickup {self.num} has been resolved A {self.score_a}:{self.score_b} B')
        self.state = RESOLVED
        return True

    def process_warnings(self):
        if not self.warnings:
            return None
        result = self.warnings.copy()
        self.warnings = set()
        return result

    def cancel(self):
        self.state = CANCELLED
