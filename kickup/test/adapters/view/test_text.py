from adapters.view.text import Text
from domain.teamboard import Teamboard, Teamscore
from test.util import *


class TestText:

    def test_rendering_a_simple_example_throws_no_errors(self):
        Text().render_teamboard(Teamboard([
            Teamscore(dirk, alex, 100, 20),
            Teamscore(alex, dirk, 80, 30),
            Teamscore(felix, tobi, 70, 30),
            Teamscore(tobi, felix, 90, 60),
        ]))
