from dataclasses import dataclass
from kickup.domain.entities import PickupMatch, PickupMatchStatus, Player


@dataclass(frozen=True)
class SlackPlayerDTO:
    name: str
    slack_id: str
    _id: str = None


@dataclass
class SlackPairingDTO:
    goal_A: SlackPlayerDTO
    strike_A: SlackPlayerDTO

    goal_B: SlackPlayerDTO
    strike_B: SlackPlayerDTO


OPEN = "open"
RUNNING = "running"
RESOLVED = "resolved"
CANCELLED = "cancelled"


# This should be the slack 'DTO' for pickup matches
class SlackPickupMatchTDO:
    def __init__(self, num):
        self.num = num
        self.state = OPEN
        self.players = set()
        self.pairing = None
        self.score_B = 0
        self.score_A = 0


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


def map_domain_player(domain_player: Player) -> SlackPlayerDTO:
    return SlackPlayerDTO(domain_player.name, "unmappable", domain_player.id)


def map_domain_pickup_match_pairing(pickup_match: PickupMatch) -> SlackPairingDTO:
    # if one field's missing, there shouldn't be any other position fields set
    if pickup_match.a_goalie is None:
        return None
    return SlackPairingDTO(
        map_domain_player(pickup_match.a_goalie),
        map_domain_player(pickup_match.a_striker),
        map_domain_player(pickup_match.b_goalie),
        map_domain_player(pickup_match.b_striker),
    )


def map_domain_pickup_match_to_slack_dto(
    pickup_match: PickupMatch,
) -> SlackPickupMatchTDO:
    k = SlackPickupMatchTDO(pickup_match.id)
    k.state = map_domain_state(pickup_match.status)
    k.players = set(pickup_match.candidates)

    k.pairing = map_domain_pickup_match_pairing(pickup_match)
    k.score_A = pickup_match.a_score
    k.score_B = pickup_match.b_score
    return k
