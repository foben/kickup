from flask import Flask

from kickup.adapters.firestore_repositories import FirestorePlayerRepository, FirestoreMatchResultRepository
from kickup.adapters.inmemory_repositories import InMemoryPickupMatchRepository, InMemoryPlayerRepository, \
    InMemoryMatchResultRepository

flask_app = Flask(__name__)


class KickUpApp:

    def __init__(self, pickup_match_repository, player_repository, match_result_repository):
        self.pickup_match_repository = pickup_match_repository
        self.player_repository = player_repository
        self.match_result_repository = match_result_repository


player_repo = FirestorePlayerRepository()
kickup_app = KickUpApp(
    InMemoryPickupMatchRepository(),
    player_repo,
    InMemoryMatchResultRepository(),
    # FirestoreMatchResultRepository(player_repo),
)

import kickup.endpoints
