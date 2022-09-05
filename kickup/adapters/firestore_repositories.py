import datetime
import logging
from dataclasses import dataclass, asdict
from uuid import UUID
from typing import List
from google.cloud import firestore
from google.cloud.firestore_v1 import DocumentSnapshot

from kickup.domain.entities import MatchResultDouble, Player
from kickup.domain.repositories import MatchResultRepository, PlayerRepository


class FirestorePlayerRepository(PlayerRepository):
    @classmethod
    def map_firestore_dict(cls, fstore_player: DocumentSnapshot) -> Player:
        return Player(
            UUID(fstore_player.id),
            fstore_player.to_dict()["name"],
        )

    def __init__(self):
        logging.debug("Setting up Firestore client for PlayerRepository")
        # TODO: inject
        self.fstore = firestore.Client(project="kickup-360018")
        self.by_id_cache = {}
        logging.info("player repo seems ok")

    def by_id(self, player_id: UUID) -> Player:
        if not isinstance(player_id, UUID):
            raise ValueError("please provide id as UUID")

        if player_id not in self.by_id_cache:
            p_doc = self.fstore.collection("players").document(str(player_id)).get()
            if not p_doc.exists:
                raise ValueError(f"Player with id {player_id} not found")
            assert player_id == UUID(p_doc.id)

            player = FirestorePlayerRepository.map_firestore_dict(p_doc)
            self.by_id_cache[player_id] = player

        return self.by_id_cache[player_id]

    def create_update(self, player: Player):
        # TODO: update cache!
        raise NotImplementedError

    # TODO: use Optionals ?
    def by_external_id(self, external_id_type, external_id) -> Player:
        if external_id_type != "slack":
            raise NotImplementedError(f"unknown id type '{external_id_type}''")
        query_ref = self.fstore.collection("players").where(
            "external_id_slack", "==", external_id
        )
        results = [x for x in query_ref.stream()]
        if len(results) < 1:
            logging.info(
                f"no results for external '{external_id_type}' id '{external_id}'"
            )
            return None
        elif len(results) > 1:
            logging.warning(
                f"got ambiguous result for external '{external_id_type}' id '{external_id}': {len(results)} matches"
            )
            return None
        return FirestorePlayerRepository.map_firestore_dict(results[0])


@dataclass
class FirestoreMatchResultDao:
    a_goalie: str
    a_striker: str
    b_goalie: str
    b_striker: str
    a_score: int
    b_score: int
    date: datetime.datetime


class FirestoreMatchResultRepository(MatchResultRepository):
    def __init__(self, player_repo: FirestorePlayerRepository):
        self.player_repository = player_repo
        logging.debug("Setting up Firestore client for MatchResultRepository")
        # TODO: inject
        self.fstore = firestore.Client(project="kickup-360018")

    def all_double_results(self) -> List[MatchResultDouble]:
        logging.debug("retrieving all matches from GCP firestore")

        match_coll = self.fstore.collection("matches")
        # match_docs = match_coll.stream()
        all_matches = []
        for match in match_coll.stream():
            match_dict = match.to_dict()
            # TODO: drop match and log warning when player can't be resolved
            r = MatchResultDouble(
                self.player_repository.by_id(UUID(match_dict["a_goalie"])),
                self.player_repository.by_id(UUID(match_dict["a_striker"])),
                self.player_repository.by_id(UUID(match_dict["b_goalie"])),
                self.player_repository.by_id(UUID(match_dict["b_striker"])),
                match_dict["a_score"],
                match_dict["b_score"],
                match_dict["date"],
                UUID(match.id),
            )
            all_matches.append(r)
        return all_matches

    def save_double_result(self, match_result: MatchResultDouble):
        dao = FirestoreMatchResultDao(
            str(match_result.a_goalie.id),
            str(match_result.a_striker.id),
            str(match_result.b_goalie.id),
            str(match_result.b_striker.id),
            match_result.a_score,
            match_result.b_score,
            match_result.date
        )
        logging.info(f"writing match result {match_result.id} to database")
        self.fstore.collection("matches").document(str(match_result.id)).set(
            asdict(dao)
        )
        logging.info(f"successfully written match result {match_result.id} to database")
