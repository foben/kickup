from kickup import flask_app, kickup_app

from flask import request, g
from kickup import api, delayed
import json

from kickup.domain.usecases.leaderboard import LeaderboardUsecase
from kickup.domain.usecases.pickupmatch import PickupMatchUsecase
from kickup.domain.usecases.playermapping import PlayerMappingUsecase
from kickup.persistence import persistence
from logging.config import dictConfig
import logging

from kickup.persistence.state import map_domain_pickup_match_to_slack_dto

dictConfig({
    'version': 1,
    'formatters': {'default': {
        'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
    }},
    'handlers': {'wsgi': {
        'class': 'logging.StreamHandler',
        'stream': 'ext://flask.logging.wsgi_errors_stream',
        'formatter': 'default'
    }},
    'root': {
        'level': 'DEBUG',
        'handlers': ['wsgi']
    }
})


@flask_app.route("/api/slash", methods=['GET', 'POST'])
def hello():
    logging.info("slash request received")
    if not 'text' in request.form or request.form['text'] == "":
        logging.debug(f'Received invalid command')
        return api.error_response('Invalid command')
    command, _, _ = request.form['text'].strip().partition(' ')
    if command == 'new':
        pickup_match = PickupMatchUsecase(
            kickup_app.pickup_match_repository,
            kickup_app.player_repository,
            kickup_app.match_result_repository).create_pickup_match()
        mapped_pickup = map_domain_pickup_match_to_slack_dto(pickup_match)
        logging.info(f'Created new kickup with identifier { mapped_pickup.num }')
        return api.respond(mapped_pickup)
    elif command == 'elo':
        uc = LeaderboardUsecase(kickup_app.match_result_repository)
        leaderboard = uc.calculate()
        # leaderboard = elo.leaderboard(persistence.matches_sorted())
        return api.elo_leaderboard_resp(leaderboard)
    else:
        return api.error_response(f'Invalid command: "{ command }"')


@flask_app.route("/api/interactive", methods=['GET', 'POST'])
def interactive():
    payload = json.loads(request.form['payload'])
    user_slack_id = payload['user']['id']
    # g.context_player = set_context_player(user_slack_id)

    # kickup_num = int(payload['callback_id'])
    # kickup = st.get_kickup(kickup_num)

    # if not kickup:
    #     logging.warning(f'Could not find kickup with id { kickup_num }')
    #     return api.respond(None)

    pickup_match_id = payload['callback_id']
    response_kickup = None
    action = payload['actions'][0]

    uc_pickup = PickupMatchUsecase(
        kickup_app.pickup_match_repository,
        kickup_app.player_repository,
        kickup_app.match_result_repository
    )

    # TODO: during refactoring, all cases were thrown together in this one if-else monster
    # TODO: split and refactor response-dto handling
    try:
        ################################
        # A score for a team was set
        if action['type'] == 'select':
            action_name = action['name']
            if action_name not in ('score_A', 'score_B'):
                logging.warning(f'Received unknown select action "{action_name}"')
                return

            new_score = int(action['selected_options'][0]['value'])

            if action_name == 'score_A':
                logging.info(f'New score for team A in kickup {pickup_match_id} is {new_score}')
                pickup_match = uc_pickup.set_team_a_score(pickup_match_id, new_score)
                response_kickup = map_domain_pickup_match_to_slack_dto(pickup_match)
            elif action_name == 'score_B':
                logging.info(f'New score for team B in kickup {pickup_match_id} is {new_score}')
                pickup_match = uc_pickup.set_team_b_score(pickup_match_id, new_score)
                response_kickup = map_domain_pickup_match_to_slack_dto(pickup_match)

        ################################
        # One of the buttons was pressed
        else:
            uc_playermap = PlayerMappingUsecase(kickup_app.player_repository)
            player = uc_playermap.get_player_for_external_id("slack", user_slack_id)
            if not player:
                # TODO: handle errors gracefully
                raise ValueError(f"unable to get internal player id for this external id")

            button_cmd = action['value']
            if button_cmd == 'join':
                pickup_match = uc_pickup.join_pickup_match(pickup_match_id, player.id)
                response_kickup = map_domain_pickup_match_to_slack_dto(pickup_match)
            elif button_cmd == 'dummyadd':

                uc_pickup.join_pickup_match(pickup_match_id, uc_playermap.get_player_for_external_id("slack", "UD12PG33M").id)
                uc_pickup.join_pickup_match(pickup_match_id, uc_playermap.get_player_for_external_id("slack", "UD276006T").id)
                uc_pickup.join_pickup_match(pickup_match_id, uc_playermap.get_player_for_external_id("slack", "UCYCRPM37").id)
                pickup_match = uc_pickup.join_pickup_match(pickup_match_id, uc_playermap.get_player_for_external_id("slack", "UFL1ME8S1").id)
                response_kickup = map_domain_pickup_match_to_slack_dto(pickup_match)
            elif button_cmd == 'cancel':
                pickup_match = uc_pickup.cancel_pickup_match(pickup_match_id)
                response_kickup = map_domain_pickup_match_to_slack_dto(pickup_match)
            elif button_cmd == 'start':
                pickup_match = uc_pickup.start_pickup_match(pickup_match_id)
                response_kickup = map_domain_pickup_match_to_slack_dto(pickup_match)
            elif button_cmd == 'resolve':
                pickup_match = uc_pickup.resolve_match(pickup_match_id)
                response_kickup = map_domain_pickup_match_to_slack_dto(pickup_match)

                # if kickup.resolve_match():
                #     logging.info(f'Kickup {kickup.num} resolved, persisting to DB')
                #     persistence.save_kickup_match(kickup)

    except KickupException as ke:
        delayed.delayed_error(ke, payload['response_url'])
        logging.error(ke)
    finally:
        return api.respond(response_kickup)


# def set_context_player(user_slack_id):
#     player = persistence.player_by_slack_id(user_slack_id)
#     def context_player():
#         if not player:
#             raise KickupException(f'Could not find registered player with your Slack ID!')
#         return player
#     return context_player

class KickupException(Exception):
    pass
#
# if __name__ == '__main__':
#     app.run(debug=True, host='0.0.0.0', port=8000)
