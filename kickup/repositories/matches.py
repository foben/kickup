from abc import ABC, abstractmethod


class Matches(ABC):

    @abstractmethod
    def all(self):
        """" returns all matches sorted by date ascending """
        pass

    @abstractmethod
    def since(self, timestamp):
        """" returns all matches sorted by date ascending """
        pass

    @abstractmethod
    def last(self, count):
        """" returns all matches sorted by date ascending """
        pass
