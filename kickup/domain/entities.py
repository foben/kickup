import datetime
from dataclasses import dataclass
from typing import List
from enum import Enum


@dataclass(frozen=True)
class Player:
    id: str
    name: str


@dataclass
class MatchResultDouble:
    id: str
    a_goalie: Player
    a_striker: Player
    b_goalie: Player
    b_striker: Player
    a_score: int
    b_score: int
    date: datetime.date


class PickupMatchStatus(Enum):
    OPEN = 1
    STARTED = 2
    RESOLVED = 3
    CANCELED = 4


@dataclass
class PickupMatch:
    id: str
    candidates: List[Player]
    status: PickupMatchStatus




