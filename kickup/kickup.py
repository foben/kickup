from flask import Flask, request, jsonify
import state as st
import api
import json
import pack
app = Flask(__name__)


@app.route("/kickup", methods=['GET', 'POST'])
def hello():
    print(request.form)
    command, _, args = request.form['text'].strip().partition(' ')
    if not command == 'new':
        return invalid_command(command)
    else:
        return api.respond(st.new_kickup())

@app.route("/interactive", methods=['GET', 'POST'])
def interactive():
    print(request.form)
    payload = json.loads(request.form['payload'])
    kickup_num = int(payload['callback_id'])
    kickup = st.get_kickup(kickup_num)
    if not kickup:
        print(f'Could not find kickup with id { kickup_num }')
        return None
    action = payload['actions'][0]
    if action['type'] == 'select':
        handle_select(kickup, action)
    else:
        handle_button(payload, kickup, action)

    return api.respond(kickup)

def handle_select(kickup, action):
    if action['name'] == 'score_blue':
        kickup.score_blue = int(action['selected_options'][0]['value'])
    elif action['name'] == 'score_red':
        kickup.score_red = int(action['selected_options'][0]['value'])
    pass

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
            pack.packeroo_match(kickup)

def invalid_command(command):
    return jsonify( {
            'response_type': 'ephemeral',
            'text': 'Sorry, I don\'t know what "{ command }" means',
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=80)
