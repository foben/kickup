from kickup.domain.entities import MatchResultDouble
from kickup.domain.repositories import MatchResultRepository


class InMemoryMatchResultRepository(MatchResultRepository):
    def all_double_results(self) -> MatchResultDouble:
        pass

    def save_double_result(self, match_result):
        pass

