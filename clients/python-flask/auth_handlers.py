import time
import urllib.parse

import jwt
import requests

from config import config

COGNITO_CLIENT_ID = config["COGNITO_CLIENT_ID"]
COGNITO_CLIENT_SECRET = config["COGNITO_CLIENT_SECRET"]
REDIRECT_URI = config["REDIRECT_URI"]
HOSTEDUIPATH = config["HOSTEDUIPATH"]

cognito_login_path = f"{HOSTEDUIPATH}/oauth2/authorize?client_id={COGNITO_CLIENT_ID}&response_type=code&scope=aws.cognito.signin.user.admin+email+openid+phone+profile&redirect_uri={urllib.parse.quote(REDIRECT_URI)}"
token_url = f"{HOSTEDUIPATH}/oauth2/token"

def token_is_valid(token):
    """Decode and check that the token is still valid."""
    if not token:
        return False

    jwt_data = jwt.decode(token, options={"verify_signature": False})
    if jwt_data.get("exp") < int(time.time()):
        return False
    return True


class CodeExchangeException(Exception):
    pass

def exchange_auth_code_for_tokens(code):
    auth = requests.auth.HTTPBasicAuth(COGNITO_CLIENT_ID, COGNITO_CLIENT_SECRET)

    params = {
        "grant_type": "authorization_code",
        "client_id": COGNITO_CLIENT_ID,
        "code": code,
        "redirect_uri": REDIRECT_URI
    }

    response = requests.post(token_url, auth=auth, data=params)
    response.raise_for_status()

    json_response = response.json()

    id_token = json_response["id_token"]
    access_token = json_response["access_token"]
    refresh_token = json_response["refresh_token"]

    return id_token, access_token, refresh_token


def exchange_refresh_token_for_tokens(refresh_token):
    auth = requests.auth.HTTPBasicAuth(COGNITO_CLIENT_ID, COGNITO_CLIENT_SECRET)

    params = {
        "grant_type": "refresh_token",
        "client_id": COGNITO_CLIENT_ID,
        "refresh_token": refresh_token,
    }

    response = requests.post(token_url, auth=auth, data=params)
    response.raise_for_status()

    json_response = response.json()

    id_token = json_response["id_token"]
    access_token = json_response["access_token"]
    # You don't get a new refresh token - you keep using the same one

    return id_token, access_token