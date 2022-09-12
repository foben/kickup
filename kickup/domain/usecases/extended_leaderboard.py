import datetime as dt
import logging
from collections import defaultdict


from kickup.domain.entities import MatchResultDouble, Player
from kickup.domain.repositories import MatchResultRepository
from kickup.domain.usecases.leaderboard import EloGoalDiffScore


class PlayerStats:

    def __init__(self, initial_elo):
        self.elo = initial_elo
        self.matches = 0
        self.elo_this_week = 0
        self.elo_this_month = 0
        self.matches_last_25 = []
        self.matches_this_week = []
        self.matches_this_month = []
        now = dt.datetime.now(dt.timezone.utc)

        self.week_start = (now - dt.timedelta(days=now.weekday()))\
            .replace(hour=0, minute=0, second=0, microsecond=0)

        self.month_start = (now - dt.timedelta(days=(now.day-1))) \
            .replace(hour=0, minute=0, second=0, microsecond=0)
        pass

    def update(self, match: MatchResultDouble, elo_diff):
        self.matches += 1
        self.elo += elo_diff

        self.matches_last_25.append((match, elo_diff > 0, elo_diff))
        self.matches_last_25 = self.matches_last_25[-25:]

        if match.date < self.month_start:
            return

        self.elo_this_month += elo_diff
        self.matches_this_month.append(match)

        if match.date >= self.week_start:
            self.elo_this_week += elo_diff
            self.matches_this_week.append(match)


class ExtendedLeaderboardUsecase:

    cached_board = None

    def __init__(self, match_result_repo):
        if not isinstance(match_result_repo, MatchResultRepository):
            raise TypeError("Not a proper MatchResultRepository")
        self.match_result_repo = match_result_repo

    def get_leaderboard(self):
        if ExtendedLeaderboardUsecase.cached_board is not None:
            return ExtendedLeaderboardUsecase.cached_board

        all_matches = self.match_result_repo.all_double_results()
        logging.debug(f"calculating leaderboard based on {len(all_matches)} matches")
        sorted_matches = sorted(all_matches, key=lambda m: m.date)

        scoring = EloGoalDiffScore(K=30, F=400, initial=1000)
        board = ExtendedLeaderboard(scoring)
        for match in sorted_matches:
            board.eval_match(match)

        # TODO: properly implement cache
        ExtendedLeaderboardUsecase.cached_board = board
        return board

    def get_player_stats(self, player: Player) -> PlayerStats:
        if player not in self.get_leaderboard().player_points:
            return None
        return self.get_leaderboard().player_points[player]


class ExtendedLeaderboard:
    def __init__(self, elo_system):
        self.elo_system = elo_system
        self.player_points = defaultdict(
            lambda: PlayerStats(self.elo_system.initial_score())
        )
        self.last_match = None
        self.last_delta = 0

    def eval_match(self, match: MatchResultDouble):

        a_elo = (
            self.player_points[match.a_goalie].elo
            + self.player_points[match.a_striker].elo
        ) / 2
        b_elo = (
            self.player_points[match.b_goalie].elo
            + self.player_points[match.b_striker].elo
        ) / 2

        a_delta, b_delta = self.elo_system.delta_score(
            a_elo, match.a_score, b_elo, match.b_score
        )
        self.player_points[match.a_goalie].update(match,  a_delta)
        self.player_points[match.a_striker].update(match,  a_delta)
        self.player_points[match.b_goalie].update(match,  b_delta)
        self.player_points[match.b_striker].update(match,  b_delta)

        self.last_match = match
        self.last_delta = abs(a_delta)
        return self

    def ordered(self):
        point_list = [
            {"player": i[0], "elo": i[1]["elo"], "matches": i[1]["matches"]}
            for i in self.player_points.items()
        ]
        return sorted(point_list, key=lambda e: e["elo"], reverse=True)

