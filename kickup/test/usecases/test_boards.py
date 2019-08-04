from datetime import datetime, timedelta

from persistence import Match
from repositories.matches import Matches
from usecases.boards import Boards
from test.util import alex, felix, dirk, florian, tobi, marvin, tabea


class TestTeamboards:

    def test_no_repositories_yield_an_empty_teamboard(self):
        pass

    def test_a_single_match_generates_a_correct_teamboard(self):
        pass

    def test_a_complex_set_of_matches_generates_a_valid_board(self):
        time = TestTeamboards.TimeSequence()

        class MockedMatches(Matches):
            def since(self, timestamp):
                pass

            def last(self, count):
                pass

            def all(self):
                return [
                    Match(alex, felix, dirk, marvin, 6, 0, time.next()),
                    Match(florian, alex, tobi, marvin, 3, 6, time.next()),
                    Match(dirk, alex, tobi, marvin, 6, 4, time.next()),
                    Match(tabea, alex, tobi, marvin, 6, 2, time.next()),
                    Match(tobi, alex, tobi, marvin, 6, 1, time.next()),
                    Match(felix, marvin, tobi, marvin, 6, 5, time.next()),
                    Match(felix, dirk, tobi, marvin, 6, 2, time.next()),
                    Match(felix, florian, tobi, marvin, 6, 5, time.next()),
                    Match(felix, dirk, tobi, marvin, 6, 5, time.next()),
                    Match(alex, tobi, felix, marvin, 6, 0, time.next()),
                ]

        board = Boards(MockedMatches()).elo_by_team()
        self.__always(board)

    @staticmethod
    def __always(board):
        assert TestTeamboards.__teams_are_unique(board)
        assert TestTeamboards.__teams_are_ordered(board)

    @staticmethod
    def __teams_are_unique(board):
        return len(board.scores) == len(set([(teamscore.player_strike, teamscore.player_goal) for teamscore in board.scores]))

    @staticmethod
    def __teams_are_ordered(board):
        scores = [team.score for team in board.scores]
        return scores == sorted(scores, reverse=True)

    class TimeSequence():
        last_date = datetime.min

        def next(self):
            self.last_date = self.last_date + timedelta(hours=1)
            return self.last_date
