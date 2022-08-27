import os
from pymongo import MongoClient
from google.cloud import firestore


def main():
    mongo_pass = os.environ['MONGO_PASS']
    mongo_client = MongoClient(host=f'mongodb://kickup:{mongo_pass}@127.0.0.1/kickup', connectTimeoutMS=2000,
                          serverSelectionTimeoutMS=3000)
    mc = 0

    fstore = firestore.Client(project='kickup-360018')

    for match in mongo_client.kickup.matches.find():
        print(match)
        match_id = str(match['_id'])
        nmatch = {

            '_id': match_id,
            'date': match['date'],
            'score_A': match['score_A'],
            'score_B': match['score_B'],
            'goal_A': str(match['goal_A']),
            'strike_A': str(match['strike_A']),
            'goal_B': str(match['goal_B']),
            'strike_B': str(match['strike_B']),
        }

        doc_ref = fstore.collection("matches").document(match_id)
        doc_ref.set(nmatch)
        print()


        mc += 1
    print(f"{mc} total matches")


if __name__ == "__main__":
    main()