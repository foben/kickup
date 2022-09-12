import os
import jwt
import logging
import requests
import uuid
import urllib.parse as lp

from flask import render_template, request, session, url_for, redirect, flash
from requests_oauthlib import OAuth2Session

from kickup import flask_app

client_id = os.environ.get("OAUTH_CLIENT_ID")
client_secret = os.environ.get("OAUTH_CLIENT_SECRET")
redirect_uri = os.environ.get("OAUTH_REDIRECT_URI")

# TODO: terrible for testing
if not client_id or not client_secret or not redirect_uri:
    raise ValueError("not all required OAuth configs in env-vars!")

OAUTH_CONFIG = {
    "scopes": ["openid",
               "profile",
               "email",
               ],
    "well_known_meta": "https://slack.com/.well-known/openid-configuration",
    "redirect_uri": redirect_uri,
    "client_id": client_id,
    "client_secret": client_secret,
}


def get_well_known_metadata():
    resp = requests.get(OAUTH_CONFIG["well_known_meta"])
    resp.raise_for_status()
    return resp.json()


def get_jwks_client():
    well_known_metadata = get_well_known_metadata()
    client = jwt.PyJWKClient(well_known_metadata["jwks_uri"])
    return client


jwks_client = get_jwks_client()


def redirect_to_login(message="you were redirected to the login page"):
    session.clear()
    flash(message)
    return redirect(url_for(".login"))


@flask_app.before_request
def verify_and_decode_token():
    if request.endpoint in [
        "login",
        "callback",
        "slack_slash_commands",
        "slack_interactive",
        "static",
    ]:
        return
    if request.endpoint is None:
        return
    if "id_token" not in session:
        logging.debug(f"no token found in session, redirecting")
        return redirect_to_login("no user session found")
    try:
        token = session["id_token"]
        signing_key = jwks_client.get_signing_key_from_jwt(token)
        header_data = jwt.get_unverified_header(token)
        jwt_decode = jwt.decode(token,
                                signing_key.key,
                                algorithms=[header_data["alg"]],
                                audience=OAUTH_CONFIG["client_id"])

        slack_id = jwt_decode["https://slack.com/user_id"]

        # slack_id = "DEBUG"
        session["slack_user"] = {"image": jwt_decode["picture"], "slack_id": slack_id}

    except Exception as e:
        logging.warning(f"exception during token validation: {type(e)}: {e}")
        return redirect_to_login("Error during authentication/authorization. Session cleared, please log in again.")


@flask_app.route("/login", methods=["GET"])
def login():
    nonce = uuid.uuid4()
    state = uuid.uuid4()
    session["nonce"] = nonce
    session["state"] = state
    return render_template("login.html", nonce=nonce, state=state, client_id=OAUTH_CONFIG["client_id"],
                           redirect_uri=OAUTH_CONFIG["redirect_uri"],
                           scopes=lp.quote(" ".join(OAUTH_CONFIG["scopes"])),
                           )


@flask_app.route("/logout", methods=["GET"])
def logout():
    return redirect_to_login("successfully logged out")


@flask_app.route("/callback", methods=["GET"])
def callback():
    meta = get_well_known_metadata()

    oauth_session = OAuth2Session(
        client_id=OAUTH_CONFIG["client_id"],
        redirect_uri=OAUTH_CONFIG["redirect_uri"],
        state=session["state"],
        scope=OAUTH_CONFIG["scopes"],
    )

    token_resp = oauth_session.fetch_token(
        meta["token_endpoint"],
        code=request.args["code"],
        client_secret=OAUTH_CONFIG["client_secret"],
    )
    if "ok" not in token_resp or not token_resp["ok"]:
        return redirect(url_for(".login"))

    session["id_token"] = token_resp["id_token"]
    return redirect(url_for(".user_profile"))
