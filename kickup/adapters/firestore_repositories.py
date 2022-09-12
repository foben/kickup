import datetime
import logging
from dataclasses import dataclass, asdict
from uuid import UUID
from typing import List
from google.cloud import firestore
from google.cloud.firestore_v1 import DocumentSnapshot

from timeit import default_timer as timer

from kickup.domain.entities import MatchResultDouble, Player, PickupMatch, PickupMatchStatus
from kickup.domain.repositories import MatchResultRepository, PlayerRepository, PickupMatchRepository


class FirestorePlayerRepository(PlayerRepository):

    @classmethod
    def map_firestore_doc(cls, fstore_player: DocumentSnapshot) -> Player:
        player_dict = fstore_player.to_dict()
        p = Player(
            UUID(fstore_player.id),
            player_dict["name"],
        )
        if "external_id_slack" in player_dict:
            p.external_ids["slack"] = player_dict["external_id_slack"]
        return p

    def __init__(self):
        logging.debug("Setting up Firestore client for PlayerRepository")
        # TODO: inject
        self.fstore = firestore.Client(project="kickup-360018")
        self.by_id_cache = {}

    def by_id(self, player_id: UUID) -> Player:
        if not isinstance(player_id, UUID):
            raise ValueError("please provide id as UUID")

        if player_id not in self.by_id_cache:
            p_doc = self.fstore.collection("players").document(str(player_id)).get()
            if not p_doc.exists:
                raise ValueError(f"Player with id {player_id} not found")
            assert player_id == UUID(p_doc.id)

            player = FirestorePlayerRepository.map_firestore_doc(p_doc)
            self.by_id_cache[player_id] = player

        return self.by_id_cache[player_id]

    def create_update(self, player: Player):
        # TODO: update cache!
        raise NotImplementedError

    # TODO: use Optionals ?
    def by_external_id(self, external_id_type, external_id) -> Player:
        if external_id_type != "slack":
            raise NotImplementedError(f"unknown id type '{external_id_type}''")

        #TODO: remove debug mapping
        if external_id == "U041FQZ3VAP":
            external_id = "UCYF8JAFL"

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
        return FirestorePlayerRepository.map_firestore_doc(results[0])


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
    def __init__(self, player_repo: PlayerRepository):
        self.player_repository = player_repo
        logging.debug("Setting up Firestore client for MatchResultRepository")
        # TODO: inject
        self.fstore = firestore.Client(project="kickup-360018")

    def map_firestore_doc(self, fstore_result: DocumentSnapshot) -> MatchResultDouble:
        match_dict = fstore_result.to_dict()
        # TODO: drop match and log warning when player can't be resolved
        r = MatchResultDouble(
            self.player_repository.by_id(UUID(match_dict["a_goalie"])),
            self.player_repository.by_id(UUID(match_dict["a_striker"])),
            self.player_repository.by_id(UUID(match_dict["b_goalie"])),
            self.player_repository.by_id(UUID(match_dict["b_striker"])),
            match_dict["a_score"],
            match_dict["b_score"],
            match_dict["date"],
            UUID(fstore_result.id),
        )
        return r

    def all_double_results(self) -> List[MatchResultDouble]:
        start = timer()
        logging.debug("retrieving all matches from firestore")

        match_coll = self.fstore.collection("matches")
        # match_docs = match_coll.stream()
        all_matches = []
        for match in match_coll.stream():
            r = self.map_firestore_doc(match)
            if r is not None:
                all_matches.append(r)
        logging.debug(f"received {len(all_matches)} matches from firestore in {timer() - start} seconds")
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

    def games_by_player(self, player: Player) -> List[MatchResultDouble]:
        results = []
        for field in ["a_goalie", "a_striker", "b_goalie", "b_striker"]:
            for r in self.fstore.collection("matches").where(field, "==", str(player.id)).stream():
                mr = self.map_firestore_doc(r)
                if r is not None:
                    results.append(mr)
        return results


@dataclass
class FirestorePickupMatchDao:
    candidates: List[str]
    status: int = 1
    a_goalie: str = None
    a_striker: str = None
    b_goalie: str = None
    b_striker: str = None
    a_score: int = 0
    b_score: int = 0


class FirestorePickupMatchRepository(PickupMatchRepository):

    def __init__(self, player_repo: PlayerRepository):
        self.player_repository: PlayerRepository = player_repo
        logging.debug("Setting up Firestore client for PickupMatchRepository")
        # TODO: inject
        self.fstore = firestore.Client(project="kickup-360018")
        self.by_id_cache = {}
        logging.info("player repo seems ok")

    def map_firestore_doc(self, fstore_match: DocumentSnapshot) -> PickupMatch:
        d = fstore_match.to_dict()
        candidates = [self.player_repository.by_id(UUID(p_id)) for p_id in d["candidates"]]

        pickup_match = PickupMatch(
            UUID(fstore_match.id),
            set(candidates),
            PickupMatchStatus(d["status"]),
            d["a_score"],
            d["b_score"],
            self.player_repository.by_id(UUID(d["a_goalie"])) if d["a_goalie"] else None,
            self.player_repository.by_id(UUID(d["a_striker"])) if d["a_striker"] else None,
            self.player_repository.by_id(UUID(d["b_goalie"])) if d["b_goalie"] else None,
            self.player_repository.by_id(UUID(d["b_striker"])) if d["b_striker"] else None,
        )

        return pickup_match

    def by_id(self, match_id: UUID) -> PickupMatch:
        if not isinstance(match_id, UUID):
            raise ValueError("please provide id as UUID")
        if match_id not in self.by_id_cache:
            m_doc = self.fstore.collection("pickup_matches").document(str(match_id)).get()
            if not m_doc.exists:
                logging.info(f"Pickup Match with id {match_id} not found")
                return None
            assert match_id == UUID(m_doc.id)
            pickup_match = self.map_firestore_doc(m_doc)
            self.by_id_cache[match_id] = pickup_match

        return self.by_id_cache[match_id]

    def create_update(self, match: PickupMatch):
        dao = FirestorePickupMatchDao(
            [str(p.id) for p in match.candidates],
            match.status.value,
            str(match.a_goalie.id) if match.a_goalie else None,
            str(match.a_striker.id) if match.a_striker else None,
            str(match.b_goalie.id) if match.b_goalie else None,
            str(match.b_striker.id) if match.b_striker else None,
            match.a_score,
            match.b_score
        )
        self.fstore.collection("pickup_matches").document(str(match.id)).set(
            asdict(dao)
        )

        self.by_id_cache[match.id] = match

