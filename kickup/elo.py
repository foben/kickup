import persistence
from collections import defaultdict

def leaderboard():
    scoring = EloGoalDiffScore(K=30, F=400, initial=1000)
    return calculate_for_all(scoring)

def calculate_for_all(scoring):
    player_points = defaultdict(lambda: {'score': scoring.initial_score(), 'count': 0})
    matches = persistence.matches_sorted()
    for match in matches:
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

#Based on the formula provided at: https://de.wikipedia.org/wiki/World_Football_Elo_Ratings
class EloGoalDiffScore():

    def __init__(self, K, F, initial):
        self.K = K
        self.F = F
        self. initial = initial

    def initial_score(self):
        return self.initial

    def delta_score(self, inputs, score_red, score_blue):
        w_red = 0 if score_red < score_blue else 1
        w_blue = 0 if score_blue < score_red else 1

        points_red = (inputs['red_goal']['points'] + inputs['red_strike']['points']) / 2
        points_blue = (inputs['blue_goal']['points'] + inputs['blue_strike']['points']) / 2
        we_red = 1 / (10**((points_blue - points_red)/self.F) + 1)
        we_blue = 1 / (10**((points_red - points_blue)/self.F) + 1)

        g = self.goal_diff_coefficient(score_red, score_blue)
        p_red = self.K * g * (w_red - we_red)
        p_blue = self.K * g * (w_blue - we_blue)
        return {
            inputs['red_goal']['id']: p_red,
            inputs['red_strike']['id']: p_red,
            inputs['blue_goal']['id']: p_blue,
            inputs['blue_strike']['id']: p_blue,
        }

    def goal_diff_coefficient(self, goals_red, goals_blue):
        score_diff = abs(goals_red - goals_blue)
        if score_diff == 0 or score_diff == 1:
            return 1
        elif score_diff == 2:
            return 1.5
        else:
            return (11 + score_diff) / 8
