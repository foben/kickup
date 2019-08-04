import numbers

import terminaltables


class Text:

    def render_score_table(self, title, table):
        view_model = terminaltables.SingleTable(table, title)
        if len(table) > 1:
            for index, value in enumerate(table[1]):
                if isinstance(value, numbers.Number):
                    view_model.justify_columns[index] = 'right'
        return view_model.table

    def render_teamboard(self, teamboard):
        return self.render_score_table(
            'Team Scores',
            [['🥅 Goalie', '👟 Striker', '💪 Elo', '💯 Games']] + \
            [[f'🥅 {teamscore.player_goal.name}', f'👟 {teamscore.player_strike.name}', teamscore.score, teamscore.game_count] for teamscore in teamboard.scores])
