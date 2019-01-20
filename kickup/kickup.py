from flask import Flask, request, jsonify
import threading
import state as st
import api
import json
import pack
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
    if not 'text' in request.form:
        return invalid_command('no-command')
    command, _, args = request.form['text'].strip().partition(' ')
    if command == 'new':
        new_kickup = st.new_kickup()
        logging.info(f'Created new kickup with identifier { new_kickup.num }')
        return api.respond(new_kickup)
    elif command == 'leaderboard':
        leaderboard = pack.packeroo_leaderboard()
        return api.leaderboard_resp(leaderboard)
    else:
        return invalid_command(command)

@app.route("/api/interactive", methods=['GET', 'POST'])
def interactive():
    payload = json.loads(request.form['payload'])
    kickup_num = int(payload['callback_id'])
    kickup = st.get_kickup(kickup_num)
    if not kickup:
        logging.warning(f'Could not find kickup with id { kickup_num }')
        return api.respond(None)
    logging.debug(f'Retrieved kickup with id { kickup_num }')
    action = payload['actions'][0]
    if action['type'] == 'select':
        handle_select(kickup, action)
    else:
        handle_button(payload, kickup, action)

    return api.respond(kickup)

def handle_select(kickup, action):
    action_name = action['name']
    if action_name not in ('score_red', 'score_blue'):
        logging.warning(f'Received unknown select action "{ action_name }"')
        return

    new_score = int(action['selected_options'][0]['value'])
    if action_name == 'score_red':
        logging.info(f'New score for team red in kickup { kickup.num } is { new_score }')
        kickup.score_red =  new_score
    elif action_name == 'score_blue':
        logging.info(f'New score for team blue in kickup { kickup.num } is { new_score }')
        kickup.score_blue = new_score

def handle_button(payload, kickup, action):
    button_cmd = action['value']
    if button_cmd == 'join':
        kickup.add_player(payload['user']['id'])
    elif button_cmd == 'dummyadd':
        kickup.add_player('UD12PG33M') #marv
        kickup.add_player('UD276006T') #ansg
        kickup.add_player('UCYCRPM37') #neiser
        kickup.add_player('UCW4HSBSM') #alex
    elif button_cmd == 'cancel':
        kickup.cancel()
    elif button_cmd == 'start':
        kickup.start_match()
    elif button_cmd == 'resolve':
        if kickup.resolve_match():
            def pack_async(kickup):
                import time
                time.sleep(3)
                logging.info(f'Start match entry for kickup { kickup.num }')
                pack.packeroo_match(kickup)
            thread = threading.Thread(target=pack_async, kwargs={'kickup': kickup})
            thread.start()
            logging.info(f'Started thread for packeroo entry of Kickup { kickup.num }')

def invalid_command(command):
    return jsonify( {
            'response_type': 'ephemeral',
            'text': f'Sorry, I don\'t know what "{ command }" means',
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=80)
