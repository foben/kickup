import persistence
from collections import defaultdict

class BaseLeaderboard:
    def __init__(self, elo_system):
        self.elo_system = elo_system
        self.player_points = defaultdict(lambda: {'elo': self.elo_system.initial_score(), 'matches': 0})
        self.last_match = None
        self.last_delta = 0

    def ordered(self):
        point_list = [{'id': i[0], 'elo': i[1]['elo'], 'matches': i[1]['matches']} for i in self.player_points.items() ]
        return sorted(point_list, key=lambda e: e['elo'], reverse=True)

class Leaderboard(BaseLeaderboard):
    def eval_match(self, match):
        elo_A = (self.player_points[match.goal_A]['elo'] + self.player_points[match.strike_A]['elo']) / 2
        elo_B = (self.player_points[match.goal_B]['elo'] + self.player_points[match.strike_B]['elo']) / 2

        delta_A, delta_B = self.elo_system.delta_score(elo_A, match.score_A, elo_B, match.score_B)
        self.player_points[match.goal_A]['elo']    += delta_A
        self.player_points[match.strike_A]['elo']  += delta_A
        self.player_points[match.goal_B]['elo']   += delta_B
        self.player_points[match.strike_B]['elo'] += delta_B

        self.player_points[match.goal_A]['matches']    += 1
        self.player_points[match.strike_A]['matches']  += 1
        self.player_points[match.goal_B]['matches']   += 1
        self.player_points[match.strike_B]['matches'] += 1

        self.last_match = match
        self.last_delta = abs(delta_A)
        return self

class Leaderboard1v1(BaseLeaderboard):
    def eval_match(self, match):
        delta_A, delta_B = self.elo_system.delta_score(
            self.player_points[match.player_A]['elo'],
            match.score_A,
            self.player_points[match.player_B]['elo'],
            match.score_B
        )
        self.player_points[match.player_A]['elo'] += delta_A
        self.player_points[match.player_B]['elo'] += delta_B

        self.player_points[match.player_A]['matches'] += 1
        self.player_points[match.player_B]['matches'] += 1

        self.last_match = match
        self.last_delta = abs(delta_A)
        return self


def leaderboard(matches):
    scoring = EloGoalDiffScore(K=30, F=400, initial=1000)
    leaderboard = Leaderboard(scoring)
    for match in matches:
        leaderboard.eval_match(match)
    return leaderboard

def leaderboard_1v1(matches_1v1):
    scoring = EloGoalDiffScore(K=30, F=400, initial=1000)
    leaderboard = Leaderboard1v1(scoring)
    for match in matches_1v1:
        leaderboard.eval_match(match)
    return leaderboard

#Based on the formula provided at: https://de.wikipedia.org/wiki/World_Football_Elo_Ratings
class EloGoalDiffScore():

    def __init__(self, K, F, initial):
        self.K = K
        self.F = F
        self. initial = initial

    def initial_score(self):
        return self.initial

    def delta_score(self, elo_A, goals_A, elo_B, goals_B):
        win_prob_A = 1 / (10**((elo_B - elo_A)/self.F) + 1)
        win_prob_B = 1 / (10**((elo_A - elo_B)/self.F) + 1)

        win_A = 0 if goals_A < goals_B else 1
        win_B = 0 if goals_B < goals_A else 1

        goal_diff_coeff = self.goal_diff_coefficient(goals_A, goals_B)
        delta_score_A = self.K * goal_diff_coeff * (win_A - win_prob_A)
        delta_score_B = self.K * goal_diff_coeff * (win_B - win_prob_B)

        return delta_score_A, delta_score_B

    def goal_diff_coefficient(self, goals_A, goals_B):
        score_diff = abs(goals_A - goals_B)
        if score_diff == 0 or score_diff == 1:
            return 1
        elif score_diff == 2:
            return 1.5
        else:
            return (11 + score_diff) / 8
