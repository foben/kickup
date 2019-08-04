from datetime import timedelta

from kickup import parse_arguments


class TestKickup:
    def test_parse_arguments(self):
        parsed_arguments = parse_arguments("teams 30d 30 other")
        assert isinstance(parsed_arguments[0], timedelta)
        assert parsed_arguments[1] == 30
        assert parsed_arguments[2] == 'other'

