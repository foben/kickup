import logging

from flask import render_template, session

from kickup import flask_app
from kickup import kickup_app
from kickup.domain.entities import MatchResultDouble
from kickup.domain.usecases.extended_leaderboard import ExtendedLeaderboardUsecase
from kickup.domain.usecases.playermapping import PlayerInfosUsecase


@flask_app.context_processor
def utility_processor():
    def color_class(amount):
        if amount < 0:
            return "has-text-danger-dark"
        elif amount > 0:
            return "has-text-success-dark"
        else:
            return ""

    def with_prefix(amount):
        if amount > 0:
            return f"+{amount}"
        else:
            return f"{amount}"

    def match_row_class(match):
        if match["won"]:
            return "has-background-success-dark"
        else:
            return "has-background-danger-dark"

    def match_tag_class(match):
        if match["won"]:
            return "is-success"
        else:
            return "is-danger"

    return dict(color_class=color_class, with_prefix=with_prefix, match_row_class=match_row_class, match_tag_class=match_tag_class)


@flask_app.route("/profile")
def user_profile():
    player_stats = {
        "total_games": -99,
        "current_elo": -99,
        "current_streak": -99,
        "elo_this_week": -9999,
        "elo_this_month": -9999,
    }

    player_uc = PlayerInfosUsecase(kickup_app.player_repository)

    slack_id = session["slack_user"]["slack_id"]
    this_player = player_uc.get_player_for_external_id("slack", slack_id)

    stats = ExtendedLeaderboardUsecase(kickup_app.match_result_repository).get_player_stats(this_player)

    last_a_goalie = stats.matches_last_25[-1][0].a_goalie
    inf = player_uc.info(last_a_goalie)

    # Matchlist transform
    last_matches = []
    mr: MatchResultDouble
    for mr, won, elo in reversed(stats.matches_last_25):
        position = "unknown"
        if this_player == mr.a_goalie:
            position = "a_goalie"
        elif this_player == mr.a_striker:
            position = "a_striker"
        elif this_player == mr.b_goalie:
            position = "b_goalie"
        elif this_player == mr.b_striker:
            position = "b_striker"
        last_matches.append({
            "won": won,
            "date": mr.date,
            "a_goalie": player_uc.info(mr.a_goalie),
            "a_striker": player_uc.info(mr.a_striker),
            "b_goalie": player_uc.info(mr.b_goalie),
            "b_striker": player_uc.info(mr.b_striker),
            "a_score": mr.a_score,
            "b_score": mr.b_score,
            "elo": int(elo),
            "position": position,
        })
    ####

    if stats is None:
        logging.warning(f"could not load any player stats for slack id '{slack_id}' ")
    else:
        player_stats["total_games"] = int(stats.matches)
        player_stats["current_elo"] = int(stats.elo)
        # player_stats["current_streak"]:
        player_stats["elo_this_week"] = int(stats.elo_this_week)
        player_stats["elo_this_month"] = int(stats.elo_this_month)

    return render_template("profile.html", slack_user=session["slack_user"], player_stats=player_stats,
                           last_matches=last_matches)
