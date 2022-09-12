#!/usr/bin/python
from time import sleep

import jinja2
import os


def url_for(endpoint, **kwargs):
    res = "#"
    if endpoint == "static" and "filename" in kwargs:
        res = f"../kickup/static/{kwargs['filename']}"
    print(f"{endpoint} + {kwargs} --> {res}")
    return res


def get_flashed_messages(*args, **kwargs):
    if kwargs and "debug" in kwargs and kwargs["debug"]:
        return ["Omg a wild debug message appeared!"]
    return None


def stat_templates():
    return (
        os.stat("../kickup/web/templates/profile.html").st_mtime,
        os.stat("../kickup/web/templates/base.html").st_mtime,
    )


slack_user = {
    "display_name": "Fooben Baringer",
    "image_192": "https://avatars.slack-edge.com/2020-11-27/1530267252165_2e3655fd6dca6ceba762_192.jpg",
    "image_512": "https://avatars.slack-edge.com/2020-11-27/1530267252165_2e3655fd6dca6ceba762_512.jpg",

}

session = {
    "access_token": "this is just a dummy",
}

last_change = None

while True:

    if stat_templates() != last_change:
        print(f"changes detected: {last_change} --> {stat_templates()}")
        last_change = stat_templates()

        templateLoader = jinja2.FileSystemLoader(searchpath="../kickup/web/templates")
        templateEnv = jinja2.Environment(loader=templateLoader)
        TEMPLATE_FILE = "profile.html"
        template = templateEnv.get_template(TEMPLATE_FILE)
        outputText = template.render(
            url_for=url_for,
            get_flashed_messages=get_flashed_messages,
            slack_user=slack_user,
            session=session,
        )

        with open("profile_dummy.html", "w") as f:
            f.write(outputText)
    else:
        pass
        # print(f"no changes: {last_change} --> {stat_templates()}")
    sleep(0.1)
