from kickup.domain.entities import Player
from kickup.domain.repositories import PickupMatchRepository, PlayerRepository


class PlayerMappingUsecase:
    def __init__(self, player_repo: PlayerRepository):
        if not isinstance(player_repo, PlayerRepository):
            raise TypeError("Not a proper PickupMatchRepository")
        self.player_repo = player_repo

    def get_player_for_external_id(self, external_id_type, external_id) -> Player:
        return self.player_repo.by_external_id(external_id_type, external_id)
