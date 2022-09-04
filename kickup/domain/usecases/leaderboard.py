import logging
from collections import defaultdict

from kickup.domain.entities import MatchResultDouble
from kickup.domain.repositories import MatchResultRepository


class LeaderboardUsecase:
    def __init__(self, match_result_repo):
        if not isinstance(match_result_repo, MatchResultRepository):
            raise TypeError("Not a proper MatchResultRepository")
        self.match_result_repo = match_result_repo

    def calculate(self):
        all_matches = self.match_result_repo.all_double_results()
        logging.debug(f"retrieved {len(all_matches)} matches from database")
        sorted_matches = sorted(all_matches, key=lambda m: m.date)

        scoring = EloGoalDiffScore(K=30, F=400, initial=1000)
        board = Leaderboard(scoring)
        for match in sorted_matches:
            board.eval_match(match)
        return board


class Leaderboard:
    def __init__(self, elo_system):
        self.elo_system = elo_system
        self.player_points = defaultdict(
            lambda: {"elo": self.elo_system.initial_score(), "matches": 0}
        )
        self.last_match = None
        self.last_delta = 0

    def eval_match(self, match: MatchResultDouble):

        a_elo = (
            self.player_points[match.a_goalie]["elo"]
            + self.player_points[match.a_striker]["elo"]
        ) / 2
        b_elo = (
            self.player_points[match.b_goalie]["elo"]
            + self.player_points[match.b_striker]["elo"]
        ) / 2

        a_delta, b_delta = self.elo_system.delta_score(
            a_elo, match.a_score, b_elo, match.b_score
        )
        self.player_points[match.a_goalie]["elo"] += a_delta
        self.player_points[match.a_striker]["elo"] += a_delta
        self.player_points[match.b_goalie]["elo"] += b_delta
        self.player_points[match.b_striker]["elo"] += b_delta

        self.player_points[match.a_goalie]["matches"] += 1
        self.player_points[match.a_striker]["matches"] += 1
        self.player_points[match.b_goalie]["matches"] += 1
        self.player_points[match.b_striker]["matches"] += 1

        self.last_match = match
        self.last_delta = abs(a_delta)
        return self

    def ordered(self):
        point_list = [
            {"player": i[0], "elo": i[1]["elo"], "matches": i[1]["matches"]}
            for i in self.player_points.items()
        ]
        return sorted(point_list, key=lambda e: e["elo"], reverse=True)


# Based on the formula provided at: https://de.wikipedia.org/wiki/World_Football_Elo_Ratings
class EloGoalDiffScore:
    def __init__(self, K, F, initial):
        self.K = K
        self.F = F
        self.initial = initial

    def initial_score(self):
        return self.initial

    def delta_score(self, elo_A, goals_A, elo_B, goals_B):
        win_prob_A = 1 / (10 ** ((elo_B - elo_A) / self.F) + 1)
        win_prob_B = 1 / (10 ** ((elo_A - elo_B) / self.F) + 1)

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
