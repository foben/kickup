from domain.teamboard import Teamscore, Teamboard
from elo import EloGoalDiffScore
from repositories.matches import Matches


class Boards:

    def __init__(self, matches: Matches, elo_calculator=EloGoalDiffScore(k=30, f=400, initial=1000)):
        self.elo_calculator = elo_calculator
        self.matches = matches

    def elo_by_team(self, using_matches=None):
        matches = self.matches.all() if using_matches is None else using_matches
        teams = dict()

        def team_keys(match):
            return (match.strike_A, match.goal_A), (match.strike_B, match.goal_B)

        def register_unknown_teams(match, teams):
            for team_key in team_keys(match):
                if teams.get(team_key, None) is None:
                    player_strike, player_goal = team_key
                    teams[team_key] = Teamscore(player_strike, player_goal, self.elo_calculator.initial, 0)

        for match in matches:
            register_unknown_teams(match, teams)
            teamscore_a, teamscore_b = tuple([teams[key] for key in team_keys(match)])
            delta_a, delta_b = self.elo_calculator.delta_score(teamscore_a.score, match.score_A, teamscore_b.score, match.score_B)
            teamscore_a.score += delta_a
            teamscore_b.score += delta_b
            teamscore_a.game_count += 1
            teamscore_b.game_count += 1

        return Teamboard(sorted(teams.values(), key=lambda team: team.score, reverse=True))

    def elo_by_teams_using_matches_since(self, timestamp):
        return self.elo_by_team(self.matches.since(timestamp))

    def elo_by_teams_using_last_matches(self, count):
        return self.elo_by_team(self.matches.last(count))
