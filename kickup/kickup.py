from flask import Flask, request, jsonify, g
import threading
import state as st
import api
import json
import elo
import persistence
import delayed
from logging.config import dictConfig
import logging

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
    if not 'text' in request.form or request.form['text'] == "":
        logging.debug(f'Received invalid command')
        return api.error_response('Invalid command')
    command, _, _ = request.form['text'].strip().partition(' ')
    if command == 'new':
        new_kickup = st.new_kickup(players_capacity=4)
        logging.info(f'Created new kickup with identifier { new_kickup.num }')
        return api.respond(new_kickup)
    elif command == '1v1':
        new_1v1_kickup = st.new_kickup(players_capacity=2)
        logging.info(f'Created new 1v1 kickup with identifier { new_1v1_kickup.num }')
        return api.respond(new_1v1_kickup)
    elif command == 'elo':
        leaderboard = elo.leaderboard(persistence.matches_sorted())
        return api.elo_leaderboard_resp(leaderboard)
    else:
        return api.error_response(f'Invalid command: "{ command }"')

@app.route("/api/interactive", methods=['GET', 'POST'])
def interactive():
    payload = json.loads(request.form['payload'])
    user_slack_id = payload['user']['id']
    # g.context_player = set_context_player(user_slack_id)
    g.context_player = persistence.Player(name="Test",slack_id=user_slack_id)

    kickup_num = int(payload['callback_id'])
    kickup = st.get_kickup(kickup_num)
    if not kickup:
        logging.warning(f'Could not find kickup with id { kickup_num }')
        return api.respond(None)
    logging.debug(f'Retrieved kickup with id { kickup_num }')
    action = payload['actions'][0]
    if not 'type' in action:
        logging.warning(f'Received malformed action: { action }')
        return api.respond(None)
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
        logging.warning(f'Received unknown select action "{ action_name }"')
        return

    new_score = int(action['selected_options'][0]['value'])
    if action_name == 'score_A':
        logging.info(f'New score for team A in kickup { kickup.num } is { new_score }')
        kickup.score_A =  new_score
    elif action_name == 'score_B':
        logging.info(f'New score for team B in kickup { kickup.num } is { new_score }')
        kickup.score_B = new_score

def handle_button(kickup, action):
    if not 'value' in action:
        logging.warning(f'Received malformed button action: { action }')
        return
    button_cmd = action['value']
    if button_cmd == 'join':
        kickup.add_player(g.context_player)
    elif button_cmd == 'dummyadd':
        kickup.add_player(persistence.player_by_slack_id('UD12PG33M')) #marv
        kickup.add_player(persistence.player_by_slack_id('UD276006T')) #ansg
        kickup.add_player(persistence.player_by_slack_id('UCYCRPM37')) #neiser
        kickup.add_player(persistence.player_by_slack_id('UFL1ME8S1')) #max
    elif button_cmd == 'cancel':
        kickup.cancel()
    elif button_cmd == 'start':
        kickup.start_match()
    elif button_cmd == 'resolve':
        if kickup.resolve_match():
            logging.info(f'Kickup { kickup.num } resolved')
            persistence.save_kickup_match(kickup)
    else:
        logging.warning(f'Received unknown button command "{ button_cmd }"')

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
