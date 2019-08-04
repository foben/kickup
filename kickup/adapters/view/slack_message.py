from attr import dataclass

from adapters.view.text import Text


@dataclass
class SlackMessage:
    text: str
    response_type: str = 'in_channel'


class SlackMessageFactory:
    text: Text

    def __init__(self, text=Text()):
        self.text = text

    def from_teamboard(self, teamboard):
        return SlackMessage(
            text=self.text.render_teamboard(teamboard)
        )
