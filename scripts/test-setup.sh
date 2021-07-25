#!/bin/sh

mongo kickup --eval 'db.createUser({user: "kickup", pwd: "secret", roles: ["readWrite"]})'

for userId in $(seq 1 10); do
  mongo kickup --eval "$(printf 'db.players.insert({"name": "User %d", "slack_id": "%d"})' $userId $userId)"
done