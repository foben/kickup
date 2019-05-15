from dataclasses import dataclass
from flask import jsonify
import state as st
import persistence

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
        return pairing(kickup, estimates=kickup.state == st.RUNNING)
    else:
        return []


def pairing(kickup, estimates=False):
    est_A = f' (max +{int(kickup.max_win_A)})' if estimates else ''
    est_B = f' (max +{int(kickup.max_win_B)})' if estimates else ''
    return [
    {
        "text": f":goal_net:<@{ kickup.pairing.goal_A.slack_id }>{est_A}\n:athletic_shoe:<@{ kickup.pairing.strike_A.slack_id }>{est_A}",
        "fallback": "Can't display this here :(",
        "callback_id": f"{ kickup.num }",
        "color": "#000000",
        "attachment_type": "default",
    },
    {
        "text": f"   VS  ",
        "fallback": "Can't display this here :(",
        "callback_id": f"{ kickup.num }",
        "attachment_type": "default",
    },
    {
        "text": f":athletic_shoe:<@{ kickup.pairing.strike_B.slack_id }>{est_B}\n:goal_net:<@{ kickup.pairing.goal_B.slack_id }>{est_B}",
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
    }[abs(kickup.score_B - kickup.score_A)]

    A_won = kickup.score_A > kickup.score_B
    A_emoji = emoji_config.winner_emoji if A_won else emoji_config.loser_emoji
    B_emoji = emoji_config.winner_emoji if not A_won else emoji_config.loser_emoji

    return f"*{ emoji_config.name }*: {A_emoji} { kickup.score_A }:{ kickup.score_B } {B_emoji}"


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
                "name": "score_A",
                "text": "Score A",
                "type": "select",
                "options": [{'text': str(i), 'value': str(i)} for i in range(7)],
                "selected_options": [ {
                    "text": str(kickup.score_A),
                    "value": str(kickup.score_A),
                    }],
                },
                {
                "name": "score_B",
                "text": "Score B",
                "type": "select",
                "options": [{'text': str(i), 'value': str(i)} for i in range(7)],
                "selected_options": [ {
                    "text": str(kickup.score_B),
                    "value": str(kickup.score_B),
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
    c2 = 13
    c3 = 5
    c4 = 5
    lines = []

    max_count = (max(map(lambda entry: int(entry["matches"]), leaderboard.ordered())))

    for idx, entry in enumerate(leaderboard.ordered()):
        player = persistence.player_by_id(entry['id'])
        pos = str(idx + 1) + '.'
        name = player.name[:c2]
        matchcount = '|' * (int(entry["matches"] / max_count / 0.20001) + 1)
        score = int(entry["elo"])
        lines.append(f'{pos:>{c1}} {name:<{c2}} {matchcount:<{c3}} {score:>{c4}}')
    lb_text = "\n".join(lines)

    pos_names = ", ".join([p.name for p in persistence.players_by_ids(leaderboard.last_match.winners())])
    neg_names = ", ".join([p.name for p in persistence.players_by_ids(leaderboard.last_match.losers())])

    pos_line = f'↗️  {pos_names:40} +{int(leaderboard.last_delta)}'
    neg_line = f'↘️  {neg_names:40} -{int(leaderboard.last_delta)}'

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
