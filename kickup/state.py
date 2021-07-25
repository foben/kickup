import random
import logging
import elo
import datetime
import copy
from dataclasses import dataclass
from persistence import Player
import persistence

KICKUPS = {}

@dataclass
class Pairing():
    goal_A: Player
    strike_A: Player

    goal_B: Player
    strike_B: Player

@dataclass
class Pairing1v1():
    player_A: Player
    player_B: Player

OPEN = 'open'
RUNNING = 'running'
RESOLVED = 'resolved'
CANCELLED = 'cancelled'

def new_kickup(players_capacity=4):
    while True:
        num = random.randint(10000,1000000)
        if num not in KICKUPS: break
    KICKUPS[num] = KickUp(num, players_capacity)
    return KICKUPS[num]

def get_kickup(num):
    if not num in KICKUPS:
        return None
    return KICKUPS[num]

class KickUp():

    def __init__(self, num, players_capacity=4):
        if not players_capacity in [2,4]:
            raise Exception(f'Invalid match size {players_capacity}!')

        self.num = num
        self.state = OPEN
        self.players = set()
        self.players_capacity = players_capacity
        self.pairing = None
        self.pairing_1v1 = None
        self.warnings = set()
        self.score_B = 0
        self.score_A = 0
        self.max_win_A = 0
        self.max_win_B = 0

    def add_player(self, player):
        if player in self.players:
            logging.info(f'Already in kickup {self.num}: { player }')
            return False
        else:
            logging.info(f'Player joined kickup {self.num}: { player }')
            self.players.add(player)
            return True

    def start_match(self):
        if len(self.players) < self.players_capacity:
            self.warnings.add(f'Need at least {self.players_capacity} players to start!')
            logging.warning(f'Kickup { self.num } needs at least {self.players_capacity} players to start!')
            return
        if self.state == RUNNING:
            logging.info('already started')
            return
        logging.info(f'Kickup Match { self.num } has been started')
        self.state = RUNNING
        if self.players_capacity == 4:
            self.pairing = Pairing(*random.sample(self.players, self.players_capacity))
        elif self.players_capacity == 2:
            self.pairing_1v1 = Pairing1v1(*random.sample(self.players, 2))
        self.set_possible_scores()

    def set_possible_scores(self):
        if self.players_capacity == 4:
            match_win_A = persistence.Match(
                self.pairing.goal_A._id,
                self.pairing.strike_A._id,
                self.pairing.goal_B._id,
                self.pairing.strike_B._id,
                6, 0,
                datetime.datetime.now(),
            )
            match_win_B = copy.deepcopy(match_win_A)
            match_win_B.score_A = 0
            match_win_B.score_B = 6
            self.max_win_A = elo.leaderboard(persistence.matches_sorted()).eval_match(match_win_A).last_delta
            self.max_win_B = elo.leaderboard(persistence.matches_sorted()).eval_match(match_win_B).last_delta
        elif self.players_capacity == 2:
            match_win_A = persistence.Match1v1(player_A=self.pairing_1v1.player_A._id, player_B=self.pairing_1v1.player_B._id, score_A=6, score_B=0, date=datetime.datetime.now())
            match_win_B = persistence.Match1v1(player_A=self.pairing_1v1.player_A._id, player_B=self.pairing_1v1.player_B._id, score_A=0, score_B=6, date=datetime.datetime.now())
            self.max_win_A = elo.leaderboard_1v1(persistence.matches_1v1_sorted()).eval_match(match_win_A).last_delta
            self.max_win_B = elo.leaderboard_1v1(persistence.matches_1v1_sorted()).eval_match(match_win_B).last_delta

    def resolve_match(self):
        if self.state == RESOLVED:
            logging.warning(f'Kickup { self.num } was resolved before!')
            return False
        if self.score_B != 6 and self.score_A != 6:
            self.warnings.add('At least one team needs 6 goals!')
            return False
        if self.score_B == 6 and self.score_A == 6:
            self.warnings.add('Both teams can\'t have score 6!')
            return False
        logging.info(f'Kickup { self.num } has been resolved A { self.score_A }:{ self.score_B } B')
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

