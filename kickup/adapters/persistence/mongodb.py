from persistence import matches_sorted
from repositories.matches import Matches


class MongoMatches(Matches):

    def all(self):
        return matches_sorted()

    def since(self, timestamp):
        return [match for match in self.all() if match.date >= timestamp]

    def last(self, count):
        return self.all()[-count:]
