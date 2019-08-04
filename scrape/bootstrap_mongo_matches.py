import datetime
import os

from pymongo import MongoClient

# Key side must correspond to names in match_list,
# Value must be name from player_list in bootstrap_mongo_users.py
name_map = {
    'foben': 'Felix',
    'QAmarv': 'Marvin',
    'asmo': 'Ansgar',
    'andreasgrub': 'Andreas',
    'alex0ptr': 'Alex',
    'dirk': 'Dirk',
    'Tim_Kiefer': 'Tim',
    'jbe': 'Jan',
    'Tabea': 'Tabea',
    'CTH': 'Christoph T.',
    'cµ': 'Christoph M.',
    'tobias': 'Tobias',
    'florianm': 'Florian',
    # ??? Maximilian
}

# List of matches to be inserted
# Originally scraped from packeroo
# No duplication check is performed!
match_list = [
    {'red_goal': 'asmo', 'red_strike': 'CTH', 'blue_goal': 'alex0ptr', 'blue_strike': 'cµ', 'score_red': 6, 'score_blue': 5},
    {'red_goal': 'alex0ptr', 'red_strike': 'Tim_Kiefer', 'blue_goal': 'asmo', 'blue_strike': 'CTH', 'score_red': 4, 'score_blue': 6},
    {'red_goal': 'asmo', 'red_strike': 'cµ', 'blue_goal': 'Tim_Kiefer', 'blue_strike': 'CTH', 'score_red': 5, 'score_blue': 6},
    {'red_goal': 'cµ', 'red_strike': 'jbe', 'blue_goal': 'Tim_Kiefer', 'blue_strike': 'asmo', 'score_red': 1, 'score_blue': 6},
    {'red_goal': 'CTH', 'red_strike': 'Tim_Kiefer', 'blue_goal': 'cµ', 'blue_strike': 'asmo', 'score_red': 6, 'score_blue': 4},
    {'red_goal': 'CTH', 'red_strike': 'asmo', 'blue_goal': 'Tim_Kiefer', 'blue_strike': 'cµ', 'score_red': 2, 'score_blue': 6},
    {'red_goal': 'alex0ptr', 'red_strike': 'andreasgrub', 'blue_goal': 'Tim_Kiefer', 'blue_strike': 'QAmarv', 'score_red': 5, 'score_blue': 6},
    {'red_goal': 'foben', 'red_strike': 'alex0ptr', 'blue_goal': 'jbe', 'blue_strike': 'Tim_Kiefer', 'score_red': 4, 'score_blue': 6},
    {'red_goal': 'asmo', 'red_strike': 'andreasgrub', 'blue_goal': 'QAmarv', 'blue_strike': 'alex0ptr', 'score_red': 6, 'score_blue': 4},
    {'red_goal': 'Tim_Kiefer', 'red_strike': 'foben', 'blue_goal': 'alex0ptr', 'blue_strike': 'QAmarv', 'score_red': 4, 'score_blue': 6},
    {'red_goal': 'asmo', 'red_strike': 'foben', 'blue_goal': 'QAmarv', 'blue_strike': 'jbe', 'score_red': 6, 'score_blue': 4},
    {'red_goal': 'foben', 'red_strike': 'asmo', 'blue_goal': 'jbe', 'blue_strike': 'QAmarv', 'score_red': 4, 'score_blue': 6},
    {'red_goal': 'QAmarv', 'red_strike': 'cµ', 'blue_goal': 'alex0ptr', 'blue_strike': 'asmo', 'score_red': 6, 'score_blue': 2},
    {'red_goal': 'QAmarv', 'red_strike': 'asmo', 'blue_goal': 'alex0ptr', 'blue_strike': 'cµ', 'score_red': 5, 'score_blue': 6},
    {'red_goal': 'andreasgrub', 'red_strike': 'cµ', 'blue_goal': 'QAmarv', 'blue_strike': 'asmo', 'score_red': 1, 'score_blue': 6},
    {'red_goal': 'Tim_Kiefer', 'red_strike': 'cµ', 'blue_goal': 'QAmarv', 'blue_strike': 'asmo', 'score_red': 4, 'score_blue': 6},
    {'red_goal': 'asmo', 'red_strike': 'alex0ptr', 'blue_goal': 'Tim_Kiefer', 'blue_strike': 'CTH', 'score_red': 6, 'score_blue': 4},
    {'red_goal': 'foben', 'red_strike': 'cµ', 'blue_goal': 'QAmarv', 'blue_strike': 'asmo', 'score_red': 0, 'score_blue': 6},
    {'red_goal': 'asmo', 'red_strike': 'cµ', 'blue_goal': 'Tim_Kiefer', 'blue_strike': 'QAmarv', 'score_red': 5, 'score_blue': 6},
    {'red_goal': 'asmo', 'red_strike': 'foben', 'blue_goal': 'dirk', 'blue_strike': 'cµ', 'score_red': 6, 'score_blue': 2},
    {'red_goal': 'dirk', 'red_strike': 'QAmarv', 'blue_goal': 'andreasgrub', 'blue_strike': 'cµ', 'score_red': 6, 'score_blue': 4},
    {'red_goal': 'alex0ptr', 'red_strike': 'dirk', 'blue_goal': 'cµ', 'blue_strike': 'Tim_Kiefer', 'score_red': 4, 'score_blue': 6},
    {'red_goal': 'alex0ptr', 'red_strike': 'cµ', 'blue_goal': 'dirk', 'blue_strike': 'foben', 'score_red': 3, 'score_blue': 6},
    {'red_goal': 'asmo', 'red_strike': 'QAmarv', 'blue_goal': 'foben', 'blue_strike': 'andreasgrub', 'score_red': 6, 'score_blue': 1},
    {'red_goal': 'andreasgrub', 'red_strike': 'cµ', 'blue_goal': 'CTH', 'blue_strike': 'jbe', 'score_red': 3, 'score_blue': 6},
    {'red_goal': 'dirk', 'red_strike': 'asmo', 'blue_goal': 'CTH', 'blue_strike': 'QAmarv', 'score_red': 6, 'score_blue': 2},
    {'red_goal': 'asmo', 'red_strike': 'cµ', 'blue_goal': 'QAmarv', 'blue_strike': 'CTH', 'score_red': 5, 'score_blue': 6},
    {'red_goal': 'cµ', 'red_strike': 'dirk', 'blue_goal': 'asmo', 'blue_strike': 'QAmarv', 'score_red': 5, 'score_blue': 6},
    {'red_goal': 'cµ', 'red_strike': 'Tabea', 'blue_goal': 'QAmarv', 'blue_strike': 'CTH', 'score_red': 1, 'score_blue': 6},
    {'red_goal': 'CTH', 'red_strike': 'dirk', 'blue_goal': 'QAmarv', 'blue_strike': 'asmo', 'score_red': 5, 'score_blue': 6},
    {'red_goal': 'CTH', 'red_strike': 'foben', 'blue_goal': 'dirk', 'blue_strike': 'cµ', 'score_red': 4, 'score_blue': 6},
    {'red_goal': 'alex0ptr', 'red_strike': 'asmo', 'blue_goal': 'foben', 'blue_strike': 'dirk', 'score_red': 6, 'score_blue': 3},
    {'red_goal': 'asmo', 'red_strike': 'dirk', 'blue_goal': 'Tim_Kiefer', 'blue_strike': 'cµ', 'score_red': 6, 'score_blue': 2},
    {'red_goal': 'Tim_Kiefer', 'red_strike': 'asmo', 'blue_goal': 'cµ', 'blue_strike': 'dirk', 'score_red': 4, 'score_blue': 6},
    {'red_goal': 'dirk', 'red_strike': 'Tim_Kiefer', 'blue_goal': 'florianm', 'blue_strike': 'asmo', 'score_red': 6, 'score_blue': 4},
    {'red_goal': 'CTH', 'red_strike': 'cµ', 'blue_goal': 'asmo', 'blue_strike': 'Tim_Kiefer', 'score_red': 3, 'score_blue': 6},
    {'red_goal': 'asmo', 'red_strike': 'CTH', 'blue_goal': 'foben', 'blue_strike': 'dirk', 'score_red': 6, 'score_blue': 2},
    {'red_goal': 'andreasgrub', 'red_strike': 'CTH', 'blue_goal': 'dirk', 'blue_strike': 'jbe', 'score_red': 2, 'score_blue': 6},
    {'red_goal': 'alex0ptr', 'red_strike': 'dirk', 'blue_goal': 'CTH', 'blue_strike': 'Tim_Kiefer', 'score_red': 6, 'score_blue': 3},
    {'red_goal': 'Tim_Kiefer', 'red_strike': 'foben', 'blue_goal': 'cµ', 'blue_strike': 'QAmarv', 'score_red': 0, 'score_blue': 6},
    {'red_goal': 'florianm', 'red_strike': 'cµ', 'blue_goal': 'Tim_Kiefer', 'blue_strike': 'QAmarv', 'score_red': 4, 'score_blue': 6},
    {'red_goal': 'dirk', 'red_strike': 'asmo', 'blue_goal': 'cµ', 'blue_strike': 'CTH', 'score_red': 5, 'score_blue': 6},
]

id_map = {}
for pack_name, mongo_name in name_map.items():
    player = player_col.find_one({'name': mongo_name})
    id_map[pack_name] = player['_id']

mongo_pw = os.environ['MONGO_PASS']
client = MongoClient(host=f'mongodb://kickup:{mongo_pw}@127.0.0.1/kickup', connectTimeoutMS=2000,
                     serverSelectionTimeoutMS=3000)
db = client.kickup
match_col = db.matches
utc_base = datetime.datetime.utcnow()
for toff, match in enumerate(match_list):
    red_goal = id_map[match['red_goal']]
    red_strike = id_map[match['red_strike']]
    blue_goal = id_map[match['blue_goal']]
    blue_strike = id_map[match['blue_strike']]
    match_time = utc_base + datetime.timedelta(seconds=toff * 2)

    mongo_match = {
        'red_goal': red_goal,
        'red_strike': red_strike,
        'blue_goal': blue_goal,
        'blue_strike': blue_strike,
        'score_red': match['score_red'],
        'score_blue': match['score_blue'],
        'date': match_time,
    }
    match_col.insert_one(mongo_match)
