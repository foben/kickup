import persistence
from collections import defaultdict

def main():
    start_points = 1000
    scoring_func = elo_scoring
    #start_points = 0
    #scoring_func = packeroo_scoring

    points = defaultdict(lambda: start_points)
    for match in persistence.matches_sorted():
        inputs = {
                'red_goal': {
                    'id': match.red_goal,
                    'points': points[match.red_goal]
                },
                'red_strike': {
                    'id': match.red_strike,
                    'points': points[match.red_strike]
                },
                'blue_goal': {
                    'id': match.blue_goal,
                    'points': points[match.blue_goal]
                },
                'blue_strike': {
                    'id': match.blue_strike,
                    'points': points[match.blue_strike]
                },
        }
        deltas = scoring_func(inputs, match.score_red, match.score_blue)
        for _id, _delta in deltas.items():
            points[_id] += _delta
    point_list = []
    for _id, _points in points.items():
        player = persistence.player_by_id(_id)
        if not player:
            continue
        point_list.append( (player.name, _points) )
    point_list = sorted(point_list, key=lambda e: e[1], reverse=True)
    for e in point_list:
        print(f'{e[0]:20}: {int(e[1]):5}')

def elo_scoring(inputs, score_red, score_blue):
    K = 30
    F = 100
    fac_red = 0 if score_red < score_blue else 1
    fac_blue = 0 if score_blue < score_red else 1
    ts_red = (inputs['red_goal']['points'] + inputs['red_strike']['points']) / 2
    ts_blue = (inputs['blue_goal']['points'] + inputs['blue_strike']['points']) / 2
    prob_red = 1 / (10**((ts_blue - ts_red)/F) + 1)
    prob_blue = 1 / (10**((ts_red - ts_blue)/F) + 1)
    #print(f'prob red : {prob_red}')
    #print(f'prob blue: {prob_blue}')
    adj_red = K * (fac_red - prob_red)
    adj_blue = K * (fac_blue - prob_blue)
    #print(f'adj red : {adj_red}')
    #print(f'adj blue : {adj_blue}')
    return {
            inputs['red_goal']['id']: adj_red,
            inputs['red_strike']['id']: adj_red,
            inputs['blue_goal']['id']: adj_blue,
            inputs['blue_strike']['id']: adj_blue,
    }



def packeroo_scoring(inputs, score_red, score_blue):
    win_score = 3
    loose_score = -2
    diff = abs(score_red - score_blue)
    if diff > 5:
        win_score = 5
        loose_score = -4
    elif diff > 3:
        win_score = 4
        loose_score = -3
    blue_score = win_score if score_red < score_blue else loose_score
    red_score = loose_score if score_red < score_blue else win_score
    return {
            inputs['red_goal']['id']: red_score,
            inputs['red_strike']['id']: red_score,
            inputs['blue_goal']['id']: blue_score,
            inputs['blue_strike']['id']: blue_score,
    }

if __name__ == '__main__':
    main()
