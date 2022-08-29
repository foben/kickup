import datetime
import uuid
from dataclasses import dataclass, field
from typing import List, Set
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
    id: str = str(uuid.uuid4())  # Should id generation be left to the adapters?
    candidates: Set[Player] = field(default_factory=set)
    status: PickupMatchStatus = PickupMatchStatus.OPEN
    a_score: int = 0
    b_score: int = 0
    a_goalie: Player = None
    a_striker: Player = None
    b_goalie: Player = None
    b_striker: Player = None





