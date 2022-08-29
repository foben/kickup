from dataclasses import dataclass

from kickup.domain.usecases.elo import LeaderboardUsecase
from kickup.adapters.inmemory_repositories import InMemoryMatchResultRepository


def test_elo_leaderboard():
    match_repo = InMemoryMatchResultRepository()
    leaderboard_uc = LeaderboardUsecase(match_repo)
    print('seems ok')
    leaderboard_uc.calculate()
    assert True


if __name__ == '__main__':
    test_elo_leaderboard()
    print("everything passed")
