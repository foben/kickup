import threading
from uuid import UUID

import requests

from kickup import flask_app, kickup_app

from flask import request
from kickup import api
import json

from kickup.api import error_response
from kickup.domain.usecases.leaderboard import LeaderboardUsecase
from kickup.domain.usecases.pickupmatch import PickupMatchUsecase
import logging

from kickup.adapters.slack import map_domain_pickup_match_to_slack_dto


@flask_app.route("/api/slash", methods=["GET", "POST"])
def slack_slash_commands():
    logging.info("slash request received")
    if not "text" in request.form or request.form["text"] == "":
        logging.debug(f"Received invalid command")
        return api.error_response("Invalid command")
    command, _, _ = request.form["text"].strip().partition(" ")
    if command == "new":
        pickup_match = PickupMatchUsecase(
            kickup_app.pickup_match_repository,
            kickup_app.match_result_repository,
        ).create_pickup_match()
        mapped_pickup = map_domain_pickup_match_to_slack_dto(pickup_match)
        logging.info(f"Created new kickup with identifier { mapped_pickup.num }")
        return api.respond(mapped_pickup)
    elif command == "elo":
        uc = LeaderboardUsecase(kickup_app.match_result_repository)
        leaderboard = uc.calculate()
        return api.elo_leaderboard_resp(leaderboard)
    else:
        return api.error_response(f'Invalid command: "{ command }"')


@flask_app.route("/api/interactive", methods=["GET", "POST"])
def slack_interactive():
    payload = json.loads(request.form["payload"])

    user_slack_id: str = payload["user"]["id"]
    pickup_match_id: UUID = UUID(payload["callback_id"])

    target_pickup_match = kickup_app.pickup_match_repository.by_id(pickup_match_id)
    if not target_pickup_match:
        logging.warning(
            f"could not get a PickupMatch for the callback_id {pickup_match_id}"
        )
        return error_response("couldn't find a PickupMatch for your request")

    acting_player = kickup_app.player_repository.by_external_id("slack", user_slack_id)
    if not acting_player:
        logging.warning(
            f"could not find a Player for the external slack-id {user_slack_id}"
        )
        return error_response("it looks like you're not set up for KickUp 😥")

    modified_pickup_match = None
    action = payload["actions"][0]

    uc_pickup = PickupMatchUsecase(
        kickup_app.pickup_match_repository,
        kickup_app.match_result_repository,
    )

    # TODO: during refactoring, all cases were thrown together in this one if-else monster
    # TODO: split and refactor response-dto handling
    try:
        ################################
        # A score for a team was set
        if action["type"] == "select":
            action_name = action["name"]
            if action_name not in ("score_A", "score_B"):
                logging.warning(f'Received unknown select action "{action_name}"')
                return

            new_score = int(action["selected_options"][0]["value"])

            if action_name == "score_A":
                logging.info(
                    f"New score for team A in kickup {target_pickup_match.id} is {new_score}"
                )
                modified_pickup_match = uc_pickup.set_team_a_score(
                    target_pickup_match, new_score
                )
            elif action_name == "score_B":
                logging.info(
                    f"New score for team B in kickup {target_pickup_match.id} is {new_score}"
                )
                modified_pickup_match = uc_pickup.set_team_b_score(
                    target_pickup_match, new_score
                )

        ################################
        # One of the buttons was pressed
        else:
            button_cmd = action["value"]
            if button_cmd == "join":
                modified_pickup_match = uc_pickup.join_pickup_match(
                    target_pickup_match, acting_player
                )
            elif button_cmd == "dummyadd":
                dummy_one = kickup_app.player_repository.by_external_id(
                    "slack", "UD12PG33M"
                )
                dummy_two = kickup_app.player_repository.by_external_id(
                    "slack", "UD276006T"
                )
                dummy_three = kickup_app.player_repository.by_external_id(
                    "slack", "UCYCRPM37"
                )
                dummy_four = kickup_app.player_repository.by_external_id(
                    "slack", "UFL1ME8S1"
                )

                uc_pickup.join_pickup_match(target_pickup_match, dummy_one)
                uc_pickup.join_pickup_match(target_pickup_match, dummy_two)
                uc_pickup.join_pickup_match(target_pickup_match, dummy_three)
                modified_pickup_match = uc_pickup.join_pickup_match(
                    target_pickup_match, dummy_four
                )

            elif button_cmd == "cancel":
                modified_pickup_match = uc_pickup.cancel_pickup_match(
                    target_pickup_match
                )
            elif button_cmd == "start":
                modified_pickup_match = uc_pickup.start_pickup_match(
                    target_pickup_match
                )
            elif button_cmd == "resolve":
                modified_pickup_match = uc_pickup.resolve_match(target_pickup_match)

    except KickupException as ke:
        delayed_error(ke, payload["response_url"])
        logging.error(ke)
    finally:
        response_dto = map_domain_pickup_match_to_slack_dto(modified_pickup_match)
        return api.respond(response_dto)


class KickupException(Exception):
    pass


def delayed_error(msg, response_url):
    def request_async(msg, response_url):
        resp = requests.post(
            response_url,
            json={
                "response_type": "ephemeral",
                "replace_original": False,
                "text": f":warning: { msg }",
            },
        )

    thread = threading.Thread(
        target=request_async, kwargs={"msg": msg, "response_url": response_url}
    )
    thread.start()
