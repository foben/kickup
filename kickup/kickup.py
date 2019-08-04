import json
import logging
from datetime import datetime, timedelta
from logging.config import dictConfig

import api
import delayed
import elo
import persistence
import state as st
from flask import Flask, request, g, jsonify

from adapters.persistence.mongodb import MongoMatches
from adapters.view.slack_message import SlackMessageFactory
from adapters.view.text import Text
from usecases.boards import Boards


class Configuration:
    """
    injects all dependencies
    """
    boards = Boards(MongoMatches())
    text = Text()
    slack = SlackMessageFactory(text)


inject = Configuration()  # for methods, where we cant inject configuration

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

app = Flask(__name__)


@app.route("/api/slash", methods=['GET', 'POST'])
def hello():
    if 'text' not in request.form or request.form['text'] == "":
        logging.debug(f'Received invalid command')
        return api.error_response('Invalid command')
    command, _, _ = request.form['text'].strip().partition(' ')
    if command == 'new':
        new_kickup = st.new_kickup()
        logging.info(f'Created new kickup with identifier {new_kickup.num}')
        return api.respond(new_kickup)
    elif command == 'elo':
        leaderboard = elo.leaderboard(persistence.matches_sorted())
        return api.elo_leaderboard_resp(leaderboard)
    elif command.startswith('teams'):
        boards = inject.boards
        teamboard = None
        arguments = parse_arguments(command)
        if len(arguments) == 0:
            teamboard = boards.elo_by_team()
        elif isinstance(arguments[0], int):
            teamboard = boards.elo_by_teams_using_last_matches(arguments[0])
        elif isinstance(arguments[0], timedelta):
            teamboard = boards.elo_by_teams_using_matches_since(datetime.today().replace(hour=0, minute=0, second=0, microsecond=0) - arguments[0])
        else:
            return api.error_response(f'Invalid parameters: "{command}"')

        return jsonify(inject.slack.from_teamboard(teamboard))
    else:
        return api.error_response(f'Invalid command: "{command}"')


def parse_arguments(command):
    def parse_argument(to_parse):
        try:
            if to_parse.endswith('d'):
                return timedelta(days=int(to_parse[:-1]))
            return int(to_parse)
        except ValueError:
            pass

        return to_parse

    return [parse_argument(argument) for argument in command.split()[1:]]


@app.route("/api/interactive", methods=['GET', 'POST'])
def interactive():
    payload = json.loads(request.form['payload'])
    user_slack_id = payload['user']['id']
    g.context_player = set_context_player(user_slack_id)

    kickup_num = int(payload['callback_id'])
    kickup = st.get_kickup(kickup_num)
    if not kickup:
        logging.warning(f'Could not find kickup with id {kickup_num}')
        return api.respond(None)
    logging.debug(f'Retrieved kickup with id {kickup_num}')
    action = payload['actions'][0]
    try:
        if action['type'] == 'select':
            handle_select(kickup, action)
        else:
            handle_button(kickup, action)
    except KickupException as ke:
        delayed.delayed_error(ke, payload['response_url'])
        logging.error(ke)
    finally:
        return api.respond(kickup)


def handle_select(kickup, action):
    action_name = action['name']
    if action_name not in ('score_A', 'score_B'):
        logging.warning(f'Received unknown select action "{action_name}"')
        return

    new_score = int(action['selected_options'][0]['value'])
    if action_name == 'score_A':
        logging.info(f'New score for team A in kickup {kickup.num} is {new_score}')
        kickup.score_A = new_score
    elif action_name == 'score_B':
        logging.info(f'New score for team B in kickup {kickup.num} is {new_score}')
        kickup.score_B = new_score


def handle_button(kickup, action):
    button_cmd = action['value']
    if button_cmd == 'join':
        kickup.add_player(g.context_player())
    elif button_cmd == 'dummyadd':
        kickup.add_player(persistence.player_by_slack_id('UD12PG33M'))  # marv
        kickup.add_player(persistence.player_by_slack_id('UD276006T'))  # ansg
        kickup.add_player(persistence.player_by_slack_id('UCYCRPM37'))  # neiser
        kickup.add_player(persistence.player_by_slack_id('UFL1ME8S1'))  # max
    elif button_cmd == 'cancel':
        kickup.cancel()
    elif button_cmd == 'start':
        kickup.start_match()
    elif button_cmd == 'resolve':
        if kickup.resolve_match():
            logging.info(f'Kickup {kickup.num} resolved, persisting to DB')
            persistence.save_kickup_match(kickup)


def set_context_player(user_slack_id):
    player = persistence.player_by_slack_id(user_slack_id)

    def context_player():
        if not player:
            raise KickupException(f'Could not find registered player with your Slack ID!')
        return player

    return context_player


class KickupException(Exception):
    pass


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)
