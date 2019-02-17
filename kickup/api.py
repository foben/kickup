from dataclasses import dataclass

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
        "text": f":goal_net:<@{ kickup.pairing.red_goal.slack_id }>\n:athletic_shoe:<@{ kickup.pairing.red_strike.slack_id }>",
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
        "text": f":athletic_shoe:<@{ kickup.pairing.blue_strike.slack_id }>\n:goal_net:<@{ kickup.pairing.blue_goal.slack_id }>",
        "fallback": "Can't display this here :(",
        "callback_id": f"{ kickup.num }",
        "color": "#0000FF",
        "attachment_type": "default",
    },
    ]

def candidate_list(kickup):
    player_list = '\n'.join([f'{ p.name }' for p in kickup.players])
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
        "text": emoji_score(kickup),
        "fallback": "Can't display this here :(",
        "callback_id": f"{ kickup.num }",
        "color": "#33CC33",
        "attachment_type": "default",
    }]


@dataclass
class EmojiWinConfig:
    name: str
    winner_emoji: str
    loser_emoji: str


def emoji_score(kickup):
    emoji_config = {
        6: EmojiWinConfig('DESTROYED', ':godmode:', ':sob:'),
        5: EmojiWinConfig('KNOCKOUT', ':punch:', ':face_with_head_bandage:'),
        4: EmojiWinConfig('MERCY', ':muscle:', ':dizzy:'),
        3: EmojiWinConfig('DOMINATED', ':stuck_out_tongue_closed_eyes:', ':astonished:'),
        2: EmojiWinConfig('NICE GAME', ':star-struck:', ':unamused:'),
        1: EmojiWinConfig('NICE GAME', ':star-struck:', ':unamused:'),
    }[abs(kickup.score_blue - kickup.score_red)]

    red_won = kickup.score_red > kickup.score_blue
    red_emoji = emoji_config.winner_emoji if red_won else emoji_config.loser_emoji
    blue_emoji = emoji_config.winner_emoji if not red_won else emoji_config.loser_emoji

    return f"*{ emoji_config.name }*: {red_emoji} { kickup.score_red }:{ kickup.score_blue } {blue_emoji}"


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
            "value": "join",
            "style": "primary",
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
            "value": "cancel",
            "style": "danger",
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
                "options": [{'text': str(i), 'value': str(i)} for i in range(7)],
                "selected_options": [ {
                    "text": str(kickup.score_red),
                    "value": str(kickup.score_red),
                    }],
                },
                {
                "name": "score_blue",
                "text": "Score Blue",
                "type": "select",
                "options": [{'text': str(i), 'value': str(i)} for i in range(7)],
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

def elo_leaderboard_resp(leaderboard):
    c1 = 3
    c2 = 15
    c3 = 2
    c4 = 5
    lines = []

    for p, e in enumerate(leaderboard['board']):
        pos = str(p + 1) + '.'
        name = e["name"][:c2]
        matchcount = e["matchcount"]
        score = int(e["score"])
        lines.append(f'{pos:>{c1}} {name:<{c2}} {matchcount:>{c3}}   {score:>{c4}}')
    lb_text = "\n".join(lines)

    last = list(filter(lambda e: e is not None, leaderboard['last']))
    pos_score = next(filter(lambda s: s >= 0, map(lambda e: e[1], last)),0)
    neg_score = next(filter(lambda s: s < 0, map(lambda e: e[1], last)),0)
    pos_names = ", ".join([e[0].name for e in filter(lambda e: e[1] >=0, last)])[0:50]
    neg_names = ", ".join([e[0].name for e in filter(lambda e: e[1] <0, last)])[0:50]

    pos_line = f'↗️  {pos_names:40} +{pos_score}'
    neg_line = f'↘️  {neg_names:40} -{abs(neg_score)}'

    res_text = f'*Elo Scores:*```\n{lb_text}```\n\n*Last Result:*\n```{pos_line}\n{neg_line}```'

    return jsonify( {
            'response_type': 'in_channel',
            'text': res_text,
    })

def error_response(error_message):
    return jsonify( {
            'response_type': 'ephemeral',
            'text': f':warning: { error_message }',
    })
