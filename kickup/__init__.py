import logging
import os
from flask import Flask

from kickup.adapters.firestore_repositories import (
    FirestorePlayerRepository,
    FirestoreMatchResultRepository, FirestorePickupMatchRepository,
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
        "disable_existing_loggers": False,
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


# Poor man's dependency injection coming up...
# this is terrible, prevents importing the kickup package


# KICKUP_MODE = "IN_MEMORY"
KICKUP_MODE = "FIRESTORE"
# KICKUP_MODE = "MIXED"

mode = os.environ.get("KICKUP_MODE")
if mode is not  None and mode not in ["IN_MEMORY", "FIRESTORE", "MIXED"]:
    KICKUP_MODE = mode

logging.info(f"Running KickUp in {KICKUP_MODE} mode")

kickup_app = None

if KICKUP_MODE == "IN_MEMORY":
    kickup_app = KickUpApp(
        InMemoryPickupMatchRepository(),
        InMemoryPlayerRepository(),
        # player_repo,
        InMemoryMatchResultRepository(),

    )
elif KICKUP_MODE == "FIRESTORE":
    # IN_MEMORY_pickup_match_repo = InMemoryPickupMatchRepository()

    firestore_player_repo = FirestorePlayerRepository()
    firestore_pickup_match_repo = FirestorePickupMatchRepository(firestore_player_repo)
    firestore_match_result_repo = FirestoreMatchResultRepository(firestore_player_repo)

    kickup_app = KickUpApp(
        firestore_pickup_match_repo,
        firestore_player_repo,
        firestore_match_result_repo
    )

elif KICKUP_MODE == "MIXED":
    IN_MEMORY_pickup_match_repo = InMemoryPickupMatchRepository()
    firestore_player_repo = FirestorePlayerRepository()
    IN_MEMORY_match_result_repo = InMemoryMatchResultRepository()

    kickup_app = KickUpApp(
        IN_MEMORY_pickup_match_repo,
        firestore_player_repo,
        IN_MEMORY_match_result_repo
    )

logging.info(f"Setting up application in {KICKUP_MODE} mode completed")

# Flask documentation says this needs to be at the bottom.
# Is this actually true?
import kickup.endpoints
