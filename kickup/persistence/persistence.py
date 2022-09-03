import datetime
import logging
import traceback
from google.cloud import firestore
from dataclasses import dataclass
from flask import g

import random, string

@dataclass(frozen=True)
class Player:
    name: str
    slack_id: str
    _id: str = None

# @dataclass
# class Match:
#     goal_A: str
#     strike_A: str
#     goal_B: str
#     strike_B: str
#     score_A: int
#     score_B: int
#     date: datetime.datetime
#     _id: str = None
#
#     def winners(self):
#         if self.score_B < self.score_A:
#             return [self.goal_A, self.strike_A]
#         else:
#             return [self.goal_B, self.strike_B]
#
#     def losers(self):
#         if self.score_B < self.score_A:
#             return [self.goal_B, self.strike_B]
#         else:
#             return [self.goal_A, self.strike_A]

# def rand_id():
#     return "fstore_" + ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(17))


# def fstore():
#     if 'fstore' not in g:
#         logging.debug('Setting up new Firestore client')
#         #TODO: inject
#         g.fstore = firestore.Client(project='kickup-360018')
#         # mongo_pass = os.environ['MONGO_PASS']
#         # g.mongo = MongoClient(host=f'mongodb://kickup:{ mongo_pass }@127.0.0.1/kickup', connectTimeoutMS=2000, serverSelectionTimeoutMS=3000)
#     # return kickup database
#     return g.fstore


# def player_by_id(player_id):
#     p = fstore().collection("players").document(player_id).get()
#     if not p.exists:
#         return None
#     return Player(**p.to_dict())

#
# def players_by_ids(obj_ids):
#     return [player for player in [player_by_id(id) for id in obj_ids] if player]


# def player_by_slack_id(slack_id):
#
#     pls = fstore().collection("players").where("slack_id", "==", slack_id).limit(1).get()
#     if len(pls) != 1:
#         return None
#     return Player(**pls[0].to_dict())


# def save_kickup_match(kickup):
#     try:
#         new_id = rand_id()
#         match = {
#             '_id': new_id,
#             'goal_A': kickup.pairing.goal_A._id,
#             'strike_A': kickup.pairing.strike_A._id,
#             'goal_B': kickup.pairing.goal_B._id,
#             'strike_B': kickup.pairing.strike_B._id,
#             'score_A': kickup.score_A,
#             'score_B': kickup.score_B,
#             'date': datetime.datetime.utcnow(),
#         }
#         logging.info(f"storing new match with id {new_id}")
#         doc_ref = fstore().collection("matches").document(new_id)
#         doc_ref.set(match)
#         logging.info(f"storing match {new_id} completed")
#
#     except Exception as e:
#         logging.error(f'Could not save kickup: {e}')
#         logging.error(traceback.format_exc())


# def matches_sorted():
#     logging.debug('retrieving all matches from database')
#
#     match_coll = fstore().collection("matches")
#     # match_docs = match_coll.stream()
#
#
#     matches = [Match(**match.to_dict()) for match in match_coll.stream()]
#     sorted_matches = sorted(matches, key=lambda m: m.date)
#     logging.debug(f'retrieved {len(sorted_matches)} matches from database')
#     return sorted_matches
