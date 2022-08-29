import logging
from abc import ABC
from typing import List
from google.cloud import firestore

from kickup.domain.entities import MatchResultDouble, Player
from kickup.domain.repositories import MatchResultRepository, PlayerRepository


class FirestorePlayerRepository(PlayerRepository):

    def __init__(self):
        logging.debug('Setting up new Firestore client')
        # TODO: inject
        self.fstore = firestore.Client(project='kickup-360018')
        self.by_id_cache = {}

    def by_id(self, player_id) -> Player:
        if player_id not in self.by_id_cache:
            p_doc = self.fstore.collection("players").document(player_id).get()
            if not p_doc.exists:
                raise ValueError(f"Player with id {player_id} not found")
            assert player_id == p_doc.id

            player = Player(
                p_doc.id,
                p_doc.to_dict()['name']
            )
            self.by_id_cache[player_id] = player

        return self.by_id_cache[player_id]

    def create_update(self, player: Player):
        # TODO: update cache!
        raise NotImplementedError


class FirestoreMatchResultRepository(MatchResultRepository):

    def __init__(self, player_repo: FirestorePlayerRepository):
        self.player_repository = player_repo
        logging.debug('Setting up new Firestore client')
        # TODO: inject
        self.fstore = firestore.Client(project='kickup-360018')

    def all_double_results(self) -> List[MatchResultDouble]:
        logging.debug('retrieving all matches from GCP firestore')

        match_coll = self.fstore.collection("matches")
        # match_docs = match_coll.stream()
        all_matches = []
        for match in match_coll.stream():
            match_dict = match.to_dict()
            r = MatchResultDouble(
                match.id,
                self.player_repository.by_id(match_dict["goal_A"]),
                self.player_repository.by_id(match_dict["strike_A"]),
                self.player_repository.by_id(match_dict["goal_B"]),
                self.player_repository.by_id(match_dict["strike_B"]),
                match_dict["score_A"],
                match_dict["score_B"],
                match_dict["date"],
            )
            all_matches.append(r)
        return all_matches

    def save_double_result(self, match_result: MatchResultDouble):
        raise NotImplementedError
