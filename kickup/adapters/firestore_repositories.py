import logging
from abc import ABC
from typing import List, Optional
from google.cloud import firestore
from google.cloud.firestore_v1 import DocumentSnapshot

from kickup.domain.entities import MatchResultDouble, Player
from kickup.domain.repositories import MatchResultRepository, PlayerRepository


class FirestorePlayerRepository(PlayerRepository):

    @classmethod
    def map_firestore_dict(cls, fstore_player: DocumentSnapshot) -> Player:
        return Player(
            fstore_player.id,
            fstore_player.to_dict()["name"],
        )

    def __init__(self):
        logging.debug('Setting up Firestore client for PlayerRepository')
        # TODO: inject
        self.fstore = firestore.Client(project='kickup-360018')
        self.by_id_cache = {}

    def by_id(self, player_id) -> Player:
        if player_id not in self.by_id_cache:
            p_doc = self.fstore.collection("players").document(player_id).get()
            if not p_doc.exists:
                raise ValueError(f"Player with id {player_id} not found")
            assert player_id == p_doc.id

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
        query_ref = self.fstore.collection("players").where("slack_id", "==", external_id)
        results = [x for x in query_ref.stream()]
        if len(results) < 1:
            logging.info(f"no results for external '{external_id_type}' id '{external_id}'")
            return None
        elif len(results) > 1:
            logging.warning(
                f"got ambiguous result for external '{external_id_type}' id '{external_id}': {len(results)} matches"
            )
            return None
        return FirestorePlayerRepository.map_firestore_dict(results[0])


class FirestoreMatchResultRepository(MatchResultRepository):

    def __init__(self, player_repo: FirestorePlayerRepository):
        self.player_repository = player_repo
        logging.debug('Setting up Firestore client for MatchResultRepository')
        # TODO: inject
        self.fstore = firestore.Client(project='kickup-360018')

    def all_double_results(self) -> List[MatchResultDouble]:
        logging.debug('retrieving all matches from GCP firestore')

        match_coll = self.fstore.collection("matches")
        # match_docs = match_coll.stream()
        all_matches = []
        for match in match_coll.stream():
            match_dict = match.to_dict()
            # TODO: drop match and log warning when player can't be resolved
            r = MatchResultDouble(
                self.player_repository.by_id(match_dict["goal_A"]),
                self.player_repository.by_id(match_dict["strike_A"]),
                self.player_repository.by_id(match_dict["goal_B"]),
                self.player_repository.by_id(match_dict["strike_B"]),
                match_dict["score_A"],
                match_dict["score_B"],
                match_dict["date"],
                match.id,
            )
            all_matches.append(r)
        return all_matches

    def save_double_result(self, match_result: MatchResultDouble):
        raise NotImplementedError
