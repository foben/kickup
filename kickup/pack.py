import requests
import bs4
import subprocess as sp
from http.cookiejar import CookieJar
import os

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


def packeroo_match(kickup):
    jar = CookieJar()
    login_token, jar = get_form_token('https://app.packeroo.de/login', jar)
    jar = get_logged_in_cookie(login_token, jar)
    match_token, jar = get_form_token('https://app.packeroo.de/matches/create/373', jar)

    create_match(jar, match_token, kickup)

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
    print(resp.headers['Location'])
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

def print_headers(res, pre='<'):
    for k, v in res.headers.items():
        print(f'{pre} {k}: {v}')

