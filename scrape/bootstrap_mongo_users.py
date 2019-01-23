import os
from pymongo import MongoClient

# List of players to add to mongo
# Duplication check performed based on slack_id
player_list = [
    {'name': 'Felix', 'slack_id': 'UCYF8JAFL', 'pack_id': '1279'},
    {'name': 'Marvin', 'slack_id': 'UD12PG33M', 'pack_id': '1261'},
    {'name': 'Ansgar', 'slack_id': 'UD276006T', 'pack_id': '1265'},
    {'name': 'Andreas', 'slack_id': 'UCYCRPM37', 'pack_id': '1286'},
    {'name': 'Alex', 'slack_id': 'UCW4HSBSM', 'pack_id': '1262'},
    {'name': 'Dirk', 'slack_id': 'UDU9HSDUK', 'pack_id': '1263'},
    {'name': 'Tim', 'slack_id': 'UCXBELFSP', 'pack_id': '1260'},
    {'name': 'Jan', 'slack_id': 'UCWLTJZAL', 'pack_id': '1281'},
    {'name': 'Tabea', 'slack_id': 'UD106404U', 'pack_id': '1304'},
    {'name': 'Christoph T.', 'slack_id': 'UCXF2T54J', 'pack_id': '1264'},
    {'name': 'Christoph M.', 'slack_id': 'UCXF74YAW', 'pack_id': '1276'},
    {'name': 'Tobias', 'slack_id': 'UFD23UJV8', 'pack_id': '1371'},
    {'name': 'Florian', 'slack_id': 'UFD4R8TDE', 'pack_id': '1372'},
    {'name': 'Maximilian', 'slack_id': 'UFL1ME8S1', '1398': '1372'},
]

mongo_pw = os.environ['MONGO_PASS']
client = MongoClient(host=f'mongodb://kickup:{ mongo_pw }@127.0.0.1/kickup', connectTimeoutMS=2000, serverSelectionTimeoutMS=3000)
db = client.kickup
player_col = db.players
for player in player_list:
    existing = player_col.find_one({'slack_id': player['slack_id']})
    if existing:
        print(f'Player { player["name"] } already in database!')
        continue
    _id = player_col.insert_one(player).inserted_id
    print(f'Player { player["name"] } was inserted with id { _id }')
