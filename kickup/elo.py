from collections import defaultdict


class Leaderboard:
    def __init__(self, elo_system):
        self.elo_system = elo_system
        self.player_points = defaultdict(lambda: {'elo': self.elo_system.initial_score(), 'matches': 0})
        self.last_match = None
        self.last_delta = 0

    def eval_match(self, match):
        elo_a = (self.player_points[match.goal_A]['elo'] + self.player_points[match.strike_A]['elo']) / 2
        elo_b = (self.player_points[match.goal_B]['elo'] + self.player_points[match.strike_B]['elo']) / 2

        delta_a, delta_b = self.elo_system.delta_score(elo_a, match.score_A, elo_b, match.score_B)
        self.player_points[match.goal_A]['elo'] += delta_a
        self.player_points[match.strike_A]['elo'] += delta_a
        self.player_points[match.goal_B]['elo'] += delta_b
        self.player_points[match.strike_B]['elo'] += delta_b

        self.player_points[match.goal_A]['matches'] += 1
        self.player_points[match.strike_A]['matches'] += 1
        self.player_points[match.goal_B]['matches'] += 1
        self.player_points[match.strike_B]['matches'] += 1

        self.last_match = match
        self.last_delta = abs(delta_a)
        return self

    def ordered(self):
        point_list = [{'id': i[0], 'elo': i[1]['elo'], 'matches': i[1]['matches']} for i in self.player_points.items()]
        return sorted(point_list, key=lambda e: e['elo'], reverse=True)


def leaderboard(matches):
    scoring = EloGoalDiffScore(k=30, f=400, initial=1000)
    leaderboard = Leaderboard(scoring)
    for match in matches:
        leaderboard.eval_match(match)
    return leaderboard


# Based on the formula provided at: https://de.wikipedia.org/wiki/World_Football_Elo_Ratings
class EloGoalDiffScore:

    def __init__(self, k, f, initial):
        self.k = k
        self.f = f
        self.initial = initial

    def initial_score(self):
        return self.initial

    def delta_score(self, elo_a, goals_a, elo_b, goals_b):
        win_prob_a = 1 / (10 ** ((elo_b - elo_a) / self.f) + 1)
        win_prob_b = 1 / (10 ** ((elo_a - elo_b) / self.f) + 1)

        win_a = 0 if goals_a < goals_b else 1
        win_b = 0 if goals_b < goals_a else 1

        goal_diff_coeff = self.goal_diff_coefficient(goals_a, goals_b)
        delta_score_a = self.k * goal_diff_coeff * (win_a - win_prob_a)
        delta_score_b = self.k * goal_diff_coeff * (win_b - win_prob_b)

        return delta_score_a, delta_score_b

    @staticmethod
    def goal_diff_coefficient(goals_a, goals_b):
        score_diff = abs(goals_a - goals_b)
        if score_diff == 0 or score_diff == 1:
            return 1
        elif score_diff == 2:
            return 1.5
        else:
            return (11 + score_diff) / 8
