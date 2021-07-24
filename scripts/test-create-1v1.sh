#!/bin/sh

NewKickup=$(curl http://localhost:8000/api/slash --form 'text=1v1' | sed 's_\\n_\\\\n_g')
echo "$NewKickup"

KickupId=$(echo "$NewKickup" | dasel -r json -w plain 'attachments.[1].callback_id')
for userId in $(seq 1 6); do
  # For this to work, you need to comment out the DB access (set_context_player)
  JoinForm=$(printf 'payload={ "user": { "id": %d }, "callback_id": %d, "actions": [{ "type": "button", "value": "join" }] }' "$userId" "$KickupId")
  curl http://localhost:8000/api/interactive --form "$JoinForm"
done

StartForm=$(printf 'payload={ "user": { "id": %d }, "callback_id": %d, "actions": [{ "type": "button", "value": "start" }] }' 999 "$KickupId")
curl http://localhost:8000/api/interactive --form "$StartForm"