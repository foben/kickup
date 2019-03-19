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
    red_goal: ObjectId
    red_strike: ObjectId
    blue_goal: ObjectId
    blue_strike: ObjectId
    score_red: int
    score_blue: int
    date: datetime.datetime
    _id: ObjectId = None

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

def player_by_slack_id(slack_id):
    player = mongo().players.find_one({ 'slack_id': slack_id })
    if not player:
        return None
    if 'pack_id' in player:
        del(player['pack_id'])
    return Player(**player)

def save_kickup_match(kickup):
    try:
        match = {
            'red_goal': kickup.pairing.red_goal._id,
            'red_strike': kickup.pairing.red_strike._id,
            'blue_goal': kickup.pairing.blue_goal._id,
            'blue_strike': kickup.pairing.blue_strike._id,
            'score_red': kickup.score_red,
            'score_blue': kickup.score_blue,
            'date': datetime.datetime.utcnow(),
        }
        mongo().matches.insert_one(match)

    except Exception as e:
        logging.error(f'Could not save kickup: {e}')
        logging.error(traceback.format_exc())


def matches_sorted():
    matches = [Match(**match) for match in mongo().matches.find()]
    sorted_matches = sorted(matches, key=lambda m: m.date)
    return sorted_matches
