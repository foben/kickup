import os
import datetime
import logging
from pymongo import MongoClient
from dataclasses import dataclass
from bson import ObjectId
from flask import g

@dataclass
class Player:
    name: str
    slack_id: str
    pack_id: str
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
    return Player(**player)

def matches_sorted():
    matches = [Match(**match) for match in mongo().matches.find()]
    return sorted(matches, key=lambda m: m.date)

