from flask import Flask

from kickup.adapters.firestore_repositories import (
    FirestorePlayerRepository,
    FirestoreMatchResultRepository,
)
from kickup.adapters.inmemory_repositories import (
    InMemoryPickupMatchRepository,
    InMemoryPlayerRepository,
    InMemoryMatchResultRepository,
)
from logging.config import dictConfig

from kickup.domain.repositories import (
    PickupMatchRepository,
    PlayerRepository,
    MatchResultRepository,
)

dictConfig(
    {
        "version": 1,
        "formatters": {
            "default": {
                "format": "[%(asctime)s] %(levelname)s in %(module)s: %(message)s",
            }
        },
        "handlers": {
            "wsgi": {
                "class": "logging.StreamHandler",
                "stream": "ext://flask.logging.wsgi_errors_stream",
                "formatter": "default",
            }
        },
        "root": {"level": "DEBUG", "handlers": ["wsgi"]},
    }
)

flask_app = Flask(__name__)


class KickUpApp:
    def __init__(
        self,
        pickup_match_repository: PickupMatchRepository,
        player_repository: PlayerRepository,
        match_result_repository: MatchResultRepository,
    ):
        self.pickup_match_repository = pickup_match_repository
        self.player_repository = player_repository
        self.match_result_repository = match_result_repository


player_repo = FirestorePlayerRepository()
kickup_app = KickUpApp(
    InMemoryPickupMatchRepository(),
    player_repo,
    # InMemoryMatchResultRepository(),
    FirestoreMatchResultRepository(player_repo),
)

import kickup.endpoints
