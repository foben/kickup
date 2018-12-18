import requests
import bs4
import subprocess as sp
from http.cookiejar import CookieJar
import os
import re
import urllib3
import logging
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

ID_MAPPINGS = {
        'UCYF8JAFL': '1279', #me
        'UD12PG33M': '1261', #marv
        'UD276006T': '1265', #ansg
        'UCYCRPM37': '1286', #grub
        'UCW4HSBSM': '1262', #alex
        'UDU9HSDUK': '1263', #dirk
        'UCXBELFSP': '1260', #tim
        'UCWLTJZAL': '1281', #jbe
        'UD106404U': '1304', #tab
        'UCXF2T54J': '1264', #cth
        'UCXF74YAW': '1276', #cmu
}

def get_slack_by_pack(pack_id):
    for slack, pack in ID_MAPPINGS.items():
        if pack == pack_id:
            return slack
    return None

def packeroo_match(kickup):
    jar = CookieJar()
    login_token, jar = get_form_token('https://app.packeroo.de/login', jar)
    jar = get_logged_in_cookie(login_token, jar)
    match_token, jar = get_form_token('https://app.packeroo.de/matches/create/373', jar)

    jar = create_match(jar, match_token, kickup)

    jar, url, resolve_token = get_resolve_url_and_token(jar)
    resolve_match(jar, url, resolve_token, kickup)
    logging.info(f'Match entry for kickup { kickup.num } complete')

def packeroo_leaderboard():
    logging.info('Retrieving Packeroo leaderboard')
    jar = CookieJar()
    login_token, jar = get_form_token('https://app.packeroo.de/login', jar)
    jar = get_logged_in_cookie(login_token, jar)

    resp = requests.get(
            'https://app.packeroo.de/leagues/373/table',
            cookies=jar,
            verify=False,
    )
    parsed = resp.json()

    leaderboard = []
    for e in parsed['data']:
        pos = e['pos']
        id_match = re.findall('https://app.packeroo.de/player/(\d*)"', e['name'])
        if id_match:
            player_id = id_match[0]
        else:
            player_id = '-1'
        points = e['points']
        leaderboard.append({
            'position': pos,
            'pack_id': player_id,
            'slack_id': get_slack_by_pack(player_id),
            'points': points,
        })
    return leaderboard

def resolve_match(jar, url, resolve_token, kickup):
    resp = requests.post(
            url,
            files = {
                '_token': (None, resolve_token),
                'result_team_one': (None, str(kickup.score_red)),
                'result_team_two': (None, str(kickup.score_blue)),
            },
            headers = {
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                'Host': 'app.packeroo.de',
                'Origin': 'https://app.packeroo.de',
                'Referer': 'https://app.packeroo.de/matches/create/373',
                'Expect': '100-continue',
            },
            cookies=jar,
            verify=False,
            allow_redirects=False,
    )


def get_resolve_url_and_token(jar):
    resp = requests.get(
            'https://app.packeroo.de/leagues/373',
            verify=False,
            allow_redirects=False,
            cookies=jar,
    )
    soup = bs4.BeautifulSoup(resp.content, 'html.parser')
    save_form = soup.find('form', {'id': 'save-score-form'})
    url = save_form.attrs['action']
    token_input = save_form.findAll('input', {'name': '_token'})[0]
    token = token_input.attrs['value']
    return resp.cookies, url, token

def create_match(jar, match_token, kickup):
    resp = requests.post(
            #'POST',
            'https://app.packeroo.de/matches',
            files = {
                '_token': (None, match_token),
                'league_id': (None, '373'),
                'position[1]': (None, ID_MAPPINGS[kickup.pairing.red_goal]),
                'position[2]': (None, ID_MAPPINGS[kickup.pairing.red_strike]),
                'position[3]': (None, ID_MAPPINGS[kickup.pairing.blue_goal]),
                'position[4]': (None, ID_MAPPINGS[kickup.pairing.blue_strike]),
                'result_team_one': (None, '6'),
                'result_team_two': (None, '4'),
            },
            headers = {
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                'Host': 'app.packeroo.de',
                'Origin': 'https://app.packeroo.de',
                'Referer': 'https://app.packeroo.de/matches/create/373',
                'Expect': '100-continue',

                #'Connection': 'keep-alive',
                #'Referer': 'https://app.packeroo.de/matches/create/373',
            },
            cookies=jar,
            verify=False,
            allow_redirects=False,
    )
    return resp.cookies


def get_logged_in_cookie(login_token, jar):
    resp = requests.post(
            'https://app.packeroo.de/login',
            cookies=jar,
            data = {
                '_token': login_token,
                'identifier': os.environ['PACK_USER'],
                'password': os.environ['PACK_PASS'],
            },
            headers = {
                #'Cookie': login_cookie,
                'Accept': '*/*',
                'Host': 'app.packeroo.de',
                'Origin': 'https://app.packeroo.de',
                'Connection': 'keep-alive',
                'Referer': 'https://app.packeroo.de/login',
            },
            verify=False,
            allow_redirects=False,
    )
    return resp.cookies

def get_form_token(url, in_jar):
    resp = requests.get(
            url,
            verify=False,
            allow_redirects=False,
            cookies=in_jar,
    )
    out_jar = resp.cookies
    soup = bs4.BeautifulSoup(resp.content, 'html.parser')
    for inp in soup.find_all('input'):
        if not inp.has_attr('name'):
            continue
        if not inp.has_attr('value'):
            continue
        if inp['name'] == '_token':
            return (inp['value'], out_jar)
    return None
