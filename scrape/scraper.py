from bs4 import BeautifulSoup

# Scrapes matches from downloaded Packeroo Matchtable-Sites named 'page_1' .. 'page_2' and prints them
# as python dicts, which can be imported to mongo with the bootstrap matches script
players = set()
totals = []
for page in range(5, 0, -1):
    sublist = []
    with open(f'page_{str(page)}') as infile:
        soup = BeautifulSoup(infile.read(), 'html.parser')
        match_rows = soup.select('div.match-row')
        for mr in match_rows:
            row = mr.find_all('div', {'class': 'row equal equal-center'})[0]
            childs = row.find_all('div', recursive=False)
            goal_red = childs[0].div.div.div.div.img['alt']
            strike_red = childs[0].div.div.next_sibling.next_sibling.div.div.img['alt']

            score_red = int(childs[2].div.div.span.string)
            score_blue = int(childs[2].div.div.span.next_sibling.next_sibling.next_sibling.next_sibling.string)

            strike_blue = childs[4].div.div.div.div.img['alt']
            goal_blue = childs[4].div.div.next_sibling.next_sibling.div.div.img['alt']

            players.add(strike_red)
            players.add(goal_red)
            players.add(strike_blue)
            players.add(goal_blue)

            dict_string = f"{{ 'red_goal': '{goal_red}', 'red_strike': '{strike_red}', 'blue_goal': '{goal_blue}', 'blue_strike': '{strike_blue}', 'score_red': {int( score_red)}, 'score_blue': {int(score_blue)}  }}"
            sublist.append(dict_string)
    totals.extend(reversed(sublist))

for t in totals:
    print(t)
