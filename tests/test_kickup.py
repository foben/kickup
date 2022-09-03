import datetime
import logging
import uuid
from dataclasses import dataclass
from uuid import UUID

from kickup.adapters.firestore_repositories import FirestorePlayerRepository, FirestoreMatchResultRepository
from kickup.domain.entities import Player, MatchResultDouble, PickupMatchStatus
from kickup.domain.usecases.leaderboard import LeaderboardUsecase
from kickup.domain.usecases.pickupmatch import PickupMatchUsecase
from kickup.adapters.inmemory_repositories import InMemoryMatchResultRepository, InMemoryPickupMatchRepository, \
    InMemoryPlayerRepository


def uid():
    return str(uuid.uuid4())


STATIC_UUIDS = [
    '196df377-305f-42ce-b0e0-163d2cb55eb9',
    'f4ea980d-d553-44d7-b6a5-43217d93167c',
    'e34034f6-a0b2-4052-a7e5-4ca8a40d081a',
    'f939cd14-72fa-43f6-8993-2c8feeb7855b',
    '61737c19-06cf-4806-bd06-76af2d42201a',
]


def logname(test_func):
    def wrapper():
        logging.info(f"Executing {test_func.__name__}")
        test_func()
    return wrapper


def dummy_players():
    return [
        Player(STATIC_UUIDS[0], "Valerio"),
        Player(STATIC_UUIDS[1], "Pepe"),
        Player(STATIC_UUIDS[2], "Letta"),
        Player(STATIC_UUIDS[3], "Antonella"),
        Player(STATIC_UUIDS[4], "Luigi"),
    ]


@logname
def test_pickup_match():
    pickup_match_repo = InMemoryPickupMatchRepository()
    player_repo = InMemoryPlayerRepository()
    match_repo = InMemoryMatchResultRepository()
    for pl in dummy_players():
        player_repo.create_update(pl)

    usecase = PickupMatchUsecase(pickup_match_repo, player_repo, match_repo)
    usecase.create_pickup_match()

    assert len(pickup_match_repo.get_all()) == 1
    _id = str(pickup_match_repo.get_all()[0].id)

    except_text = ""
    try:
        usecase.start_pickup_match(_id)
    except ValueError as e:
        except_text = str(e)
    assert except_text == "Too few players to start"

    for player_id in STATIC_UUIDS:
        usecase.join_pickup_match(_id, player_id)
    usecase.start_pickup_match(_id)

    pickup_match = pickup_match_repo.by_id(_id)
    assert pickup_match.status == PickupMatchStatus.STARTED
    assert pickup_match.a_striker.id in STATIC_UUIDS
    assert pickup_match.a_goalie.id in STATIC_UUIDS
    assert pickup_match.b_striker.id in STATIC_UUIDS
    assert pickup_match.b_goalie.id in STATIC_UUIDS


@logname
def test_elo_leaderboard():
    match_repo = InMemoryMatchResultRepository()
    p1, p2, p3, p4 = dummy_players()[:4]
    m1 = MatchResultDouble(
        p1, p2, p3, p4, 6, 0
    )
    match_repo.save_double_result(m1)

    leaderboard_uc = LeaderboardUsecase(match_repo)
    res = leaderboard_uc.calculate()
    assert True


@logname
def test_firestore_leaderboard():
    player_repo = FirestorePlayerRepository()
    match_result_repo = FirestoreMatchResultRepository(player_repo)

    leaderboard_uc = LeaderboardUsecase(match_result_repo)
    res = leaderboard_uc.calculate()
    res_sorted = sorted(list(res.player_points.items()), key=lambda it: it[1]['elo'], reverse=True)
    ct = 0
    for r in res_sorted:
        ct += 1
        print(f"{ct:2}. {r[0].name:20}{int(r[1]['elo']):4}")
    assert True


if __name__ == '__main__':
    test_firestore_leaderboard()
    test_pickup_match()
    test_elo_leaderboard()
    print("everything passed")
