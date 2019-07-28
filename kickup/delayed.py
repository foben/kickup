import threading

import requests


def delayed_error(msg, response_url):
    def request_async(msg, response_url):
        resp = requests.post(response_url, json={
            'response_type': 'ephemeral',
            'replace_original': False,
            'text': f':warning: {msg}',
        })

    thread = threading.Thread(target=request_async, kwargs={'msg': msg, 'response_url': response_url})
    thread.start()
