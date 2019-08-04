from dataclasses import dataclass
from typing import List

from persistence import Player


@dataclass
class Teamscore:
    player_strike: Player
    player_goal: Player
    score: int
    game_count: int


@dataclass
class Teamboard:
    scores: List[Teamscore]
