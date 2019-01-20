from flask import jsonify
import state as st

def respond(kickup):
    if kickup is None:
        return jsonify( {
                'response_type': 'in_channel',
                'text': ':skull_and_crossbones: Sorry, this kickup is dead',
        })
    if kickup.state == st.CANCELLED:
        return jsonify( {
                'response_type': 'in_channel',
                'text': 'This pickup match was cancelled :crying_cat_face:',
        })
    else:
        return button_resp(kickup)

def button_resp(kickup):
    if kickup.state == st.OPEN:
        text = 'Join this pickup match!'
    elif kickup.state == st.RUNNING:
        text = 'Here is the pairing for this pickup match:'
    elif kickup.state == st.RESOLVED:
        text = 'Results are in:'
    else:
        text = '? ?'
    return jsonify(
        {
            'text': text,
            'response_type': 'in_channel',
            "attachments": [
                *att_players(kickup),
                *att_buttons(kickup),
                *result(kickup),
                *att_footer(kickup),
            ]
        }
)

def att_footer(kickup):
    warnings = kickup.process_warnings()
    if not warnings:
        return []
    warn_lines = "\n".join([f':warning: { w }' for w in warnings])
    return[{
        "fallback": "Can't display this here :(",
        "callback_id": f"{ kickup.num } ",
        "footer": warn_lines,
        "color": "warning",
    }]

def att_players(kickup):
    if kickup.state == st.OPEN:
        return candidate_list(kickup)
    elif kickup.state == st.RUNNING or kickup.state == st.RESOLVED:
        return pairing(kickup)
    else:
        return []


def pairing(kickup):
    return [
    {
        "text": f":goal_net:<@{ kickup.pairing.red_goal }>\n:athletic_shoe:<@{ kickup.pairing.red_strike }>",
        "fallback": "Can't display this here :(",
        "callback_id": f"{ kickup.num }",
        "color": "#FF0000",
        "attachment_type": "default",
    },
    {
        "text": f"   VS  ",
        "fallback": "Can't display this here :(",
        "callback_id": f"{ kickup.num }",
        "color": "#000000",
        "attachment_type": "default",
    },
    {
        "text": f":athletic_shoe:<@{ kickup.pairing.blue_strike }>\n:goal_net:<@{ kickup.pairing.blue_goal }>",
        "fallback": "Can't display this here :(",
        "callback_id": f"{ kickup.num }",
        "color": "#0000FF",
        "attachment_type": "default",
    },
    ]

def candidate_list(kickup):
    player_list = '\n'.join([f'<@{ p }>' for p in kickup.players])
    return [{
        "text": f"Current players:\n{ player_list }",
        "fallback": "Can't display this here :(",
        "callback_id": f"{ kickup.num }",
        "color": "#3AA3E3",
        "attachment_type": "default",
    }]

def result(kickup):
    if kickup.state != st.RESOLVED:
        return []
    return [{
        "text": f"*RESULT:* { kickup.score_red }:{ kickup.score_blue }",
        "fallback": "Can't display this here :(",
        "callback_id": f"{ kickup.num }",
        "color": "#33CC33",
        "attachment_type": "default",
    }]

def att_buttons(kickup):
    if kickup.state == st.OPEN:
        return [{
            "callback_id": f"{ kickup.num }",
            "fallback": "OMG",
            "actions": [
            {
            "name": "kickup",
            "text": ":arrow_down: Join",
            "type": "button",
            "value": "join"
            },
            {
            "name": "kickup",
            "text": ":soccer: Start",
            "type": "button",
            "value": "start"
            },
            {
            "name": "kickup",
            "text": ":no_entry_sign: Cancel",
            "type": "button",
            "value": "cancel"
            },
            {
            "name": "kickup",
            "text": "DummyAdd",
            "type": "button",
            "value": "dummyadd"
            },
            ]
        }]
    elif kickup.state == st.RUNNING:
        return [{
            "callback_id": f"{ kickup.num }",
            "fallback": "OMG",
            "actions": [
                {
                "name": "score_red",
                "text": "Score Red",
                "type": "select",
                "options": [
                    {
                    "text": "0",
                    "value": "0"
                    },
                    {
                    "text": "1",
                    "value": "1"
                    },
                    {
                    "text": "2",
                    "value": "2"
                    },
                    {
                    "text": "3",
                    "value": "3"
                    },
                    {
                    "text": "4",
                    "value": "4"
                    },
                    {
                    "text": "5",
                    "value": "5"
                    },
                    {
                    "text": "6",
                    "value": "6"
                    },
                ],
                "selected_options": [ {
                    "text": str(kickup.score_red),
                    "value": str(kickup.score_red),
                    }],
                },
                {
                "name": "score_blue",
                "text": "Score Blue",
                "type": "select",
                "options": [
                    {
                    "text": "0",
                    "value": "0"
                    },
                    {
                    "text": "1",
                    "value": "1"
                    },
                    {
                    "text": "2",
                    "value": "2"
                    },
                    {
                    "text": "3",
                    "value": "3"
                    },
                    {
                    "text": "4",
                    "value": "4"
                    },
                    {
                    "text": "5",
                    "value": "5"
                    },
                    {
                    "text": "6",
                    "value": "6"
                    },
                ],
                "selected_options": [ {
                    "text": str(kickup.score_blue),
                    "value": str(kickup.score_blue),
                    }],
                },
                {
                "name": "kickup",
                "text": ":heavy_check_mark: Resolve",
                "type": "button",
                "value": "resolve"
                },
                {
                "name": "kickup",
                "text": ":no_entry_sign: Cancel",
                "type": "button",
                "value": "cancel"
                },
        ]}]
    else:
        return []

def leaderboard_resp(leaderboard):
    lb_text = '\n'.join([f'{x["position"]}. <@{x["slack_id"]}>   {x["points"]}' for x in leaderboard])
    return jsonify( {
            'response_type': 'in_channel',
            'text': lb_text,
    })

def elo_leaderboard_resp(leaderboard):
    lb_text = '\n'.join([f'{x["position"]:2}. {x["slack_id"]:20}   {x["points"]:5}' for x in leaderboard])
    lb_text = f'```\n{ lb_text }\n```'
    return jsonify( {
            'response_type': 'in_channel',
            'text': lb_text,
    })
