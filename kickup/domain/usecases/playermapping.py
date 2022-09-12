import logging
import os
from dataclasses import dataclass

from kickup import kickup_app
from kickup.domain.entities import Player
from kickup.domain.repositories import PickupMatchRepository, PlayerRepository

import requests


@dataclass
class PlayerInfo:
    img_url: str = kickup_app.default_avatar
    name: str = "Dummy"


class PlayerInfosUsecase:

    # TODO: proper cache
    player_info_cache = {}

    def __init__(self, player_repo: PlayerRepository):
        if not isinstance(player_repo, PlayerRepository):
            raise TypeError("Not a proper PickupMatchRepository")
        self.player_repo = player_repo
        self.slack_access_token = os.environ.get("SLACK_ACCESS_TOKEN")

    def get_player_for_external_id(self, external_id_type, external_id) -> Player:
        return self.player_repo.by_external_id(external_id_type, external_id)

    def info(self, player: Player) -> PlayerInfo:
        if player in PlayerInfosUsecase.player_info_cache:
            return PlayerInfosUsecase.player_info_cache[player]

        info = PlayerInfo()
        info.name = player.name

        if not self.slack_access_token:
            logging.warning("No Slack API credentials, cannot retrieve additional player data")
            return info
        if not player.external_ids["slack"]:
            logging.warning(f"No Slack id for player {player}, cannot retrieve additional player data")
            return info

        resp = slack_api_request("users.profile.get", self.slack_access_token, user=player.external_ids["slack"])
        if resp["ok"] and "image_512" in resp["profile"]:
            # if "is_custom_image" in resp["profile"] and resp["profile"]["is_custom_image"]:
            info.img_url = resp["profile"]["image_512"]

        PlayerInfosUsecase.player_info_cache[player] = info
        return info


def slack_api_request(method_name, access_token, **query_params):
    endpoint = f"https://slack.com/api/{method_name}"
    http_resp = requests.get(
        url=endpoint,
        headers={"Authorization": f"Bearer {access_token}"},
        params=query_params,
    )
    http_resp.raise_for_status()
    payload = http_resp.json()
    if "ok" not in payload or not payload["ok"]:
        raise ValueError(f"Slack API request failed: {payload['error']}")
    return payload
