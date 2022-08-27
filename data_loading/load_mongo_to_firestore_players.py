import os
from pymongo import MongoClient
from google.cloud import firestore


def main():
    mongo_pass = os.environ['MONGO_PASS']
    mongo_client = MongoClient(host=f'mongodb://kickup:{mongo_pass}@127.0.0.1/kickup', connectTimeoutMS=2000,
                          serverSelectionTimeoutMS=3000)
    mc = 0

    fstore = firestore.Client(project='kickup-360018')

    for player in mongo_client.kickup.players.find():
        print(player)

        pl_id = str(player['_id'])

        nplayer = {
            '_id': pl_id,
            'name': player['name'],
            'slack_id': player['slack_id']
        }

        doc_ref = fstore.collection("players").document(pl_id)
        doc_ref.set(nplayer)


        mc += 1
    print(f"{mc} total matches")


if __name__ == "__main__":
    main()