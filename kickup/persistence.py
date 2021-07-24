import os
import datetime
import logging
import traceback
from pymongo import MongoClient
from dataclasses import dataclass
from bson import ObjectId
from flask import g

@dataclass(frozen=True)
class Player:
    name: str
    slack_id: str
    _id: ObjectId = None

@dataclass
class Match:
    goal_A: ObjectId
    strike_A: ObjectId
    goal_B: ObjectId
    strike_B: ObjectId
    score_A: int
    score_B: int
    date: datetime.datetime
    _id: ObjectId = None

    def winners(self):
        if self.score_B < self.score_A:
            return [self.goal_A, self.strike_A]
        else:
            return [self.goal_B, self.strike_B]

    def losers(self):
        if self.score_B < self.score_A:
            return [self.goal_B, self.strike_B]
        else:
            return [self.goal_A, self.strike_A]


def mongo():
    if 'mongo' not in g:
        logging.debug('Setting up new MongoDB client')
        mongo_pass = os.environ['MONGO_PASS']
        g.mongo = MongoClient(host=f'mongodb://kickup:{ mongo_pass }@127.0.0.1/kickup', connectTimeoutMS=2000, serverSelectionTimeoutMS=3000)
    # return kickup database
    return g.mongo.kickup

def player_by_id(obj_id):
    player = mongo().players.find_one({ '_id': obj_id })
    if not player:
        return None
    if 'pack_id' in player:
        del(player['pack_id'])
    return Player(**player)

def players_by_ids(obj_ids):
    return [player for player in [player_by_id(id) for id in obj_ids] if player]

def player_by_slack_id(slack_id):
    player = mongo().players.find_one({ 'slack_id': slack_id })
    if not player:
        return None
    if 'pack_id' in player:
        del(player['pack_id'])
    return Player(**player)

def save_kickup_match(kickup):
    if kickup.players_capacity != 4:
        logging.info(f"Not persisting results due to match size {kickup.players_capacity}")
        return

    logging.info("Persisting results to DB")
    try:
        match = {
            'goal_A': kickup.pairing.goal_A._id,
            'strike_A': kickup.pairing.strike_A._id,
            'goal_B': kickup.pairing.goal_B._id,
            'strike_B': kickup.pairing.strike_B._id,
            'score_A': kickup.score_A,
            'score_B': kickup.score_B,
            'date': datetime.datetime.utcnow(),
        }
        mongo().matches.insert_one(match)

    except Exception as e:
        logging.error(f'Could not save kickup: {e}')
        logging.error(traceback.format_exc())


def matches_sorted():
    logging.debug('retrieving all matches from database')
    matches = [Match(**match) for match in mongo().matches.find()]
    sorted_matches = sorted(matches, key=lambda m: m.date)
    logging.debug(f'retrieved {len(sorted_matches)} matches from database')
    return sorted_matches
