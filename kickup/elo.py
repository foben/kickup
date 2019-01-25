import persistence
from collections import defaultdict

def leaderboard():
    scoring = EloScore(K=30, F=100, initial=1000)
    return calculate_for_all(scoring)

def calculate_for_all(scoring):
    player_points = defaultdict(lambda: {'score': scoring.initial_score(), 'count': 0})
    for match in persistence.matches_sorted():
        inputs = {
                'red_goal': {
                    'id': match.red_goal,
                    'points': player_points[match.red_goal]['score']
                },
                'red_strike': {
                    'id': match.red_strike,
                    'points': player_points[match.red_strike]['score']
                },
                'blue_goal': {
                    'id': match.blue_goal,
                    'points': player_points[match.blue_goal]['score']
                },
                'blue_strike': {
                    'id': match.blue_strike,
                    'points': player_points[match.blue_strike]['score']
                },
        }
        deltas = scoring.delta_score(inputs, match.score_red, match.score_blue)
        for _id, _delta in deltas.items():
            player_points[_id]['score'] += _delta
            player_points[_id]['count'] += 1
    point_list = []
    for player_id, player_aggregate in player_points.items():
        player = persistence.player_by_id(player_id)
        if not player:
            continue
        point_list.append( {
            'name': player.name,
            'score': player_aggregate['score'],
            'matchcount': player_aggregate['count'],
            })
    point_list = sorted(point_list, key=lambda e: e['score'], reverse=True)
    return {
            'board': point_list,
            'last': last_result(deltas),
    }

def last_result(delta):
    res = [(persistence.player_by_id(p), int(d)) for p, d in delta.items()]
    res.sort(key=lambda p: p[1], reverse=True)
    return res

class EloScore():

    def __init__(self, K, F, initial):
        self.K = K
        self.F = F
        self. initial = initial

    def initial_score(self):
        return self.initial

    def delta_score(self, inputs, score_red, score_blue):
        fac_red = 0 if score_red < score_blue else 1
        fac_blue = 0 if score_blue < score_red else 1
        ts_red = (inputs['red_goal']['points'] + inputs['red_strike']['points']) / 2
        ts_blue = (inputs['blue_goal']['points'] + inputs['blue_strike']['points']) / 2
        prob_red = 1 / (10**((ts_blue - ts_red)/self.F) + 1)
        prob_blue = 1 / (10**((ts_red - ts_blue)/self.F) + 1)
        adj_red = self.K * (fac_red - prob_red)
        adj_blue = self.K * (fac_blue - prob_blue)
        return {
                inputs['red_goal']['id']: adj_red,
                inputs['red_strike']['id']: adj_red,
                inputs['blue_goal']['id']: adj_blue,
                inputs['blue_strike']['id']: adj_blue,
        }


class PackerooScore():
    def __init__(self):
        pass

    def initial_score(self):
        return 0

    def delta_score(self, inputs, score_red, score_blue):
        win_score = 3
        loose_score = -2
        diff = abs(score_red - score_blue)
        if diff > 5:
            win_score = 5
            loose_score = -4
        elif diff > 3:
            win_score = 4
            loose_score = -3
        blue_score = win_score if score_red < score_blue else loose_score
        red_score = loose_score if score_red < score_blue else win_score
        return {
                inputs['red_goal']['id']: red_score,
                inputs['red_strike']['id']: red_score,
                inputs['blue_goal']['id']: blue_score,
                inputs['blue_strike']['id']: blue_score,
        }
