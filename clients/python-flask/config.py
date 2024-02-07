"""
This isn't very specific to the demo. But it sets up the constants we need to use in the demo.

The easiest thing to do is to copy the `cdk_outputs.json` file from the CDK deployment
and put it in the root of this client project.

Alternatively - you can pass the required ENV VARS before you start the app.
"""

import os
import json

STACK_NAME = os.environ.get("STACK_NAME", "CognitoPlaygroundStack")

try:
    with open("cdk_outputs.json") as f:
        config = json.load(f)[STACK_NAME]
except FileNotFoundError:
    config = {}
    print("No CDK outputs file found. You need to use ENV VARS to configure the app.")

COGNITO_CLIENT_ID = os.environ.get("COGNITO_CLIENT_ID", config.get('CognitoClientId'))
COGNITO_CLIENT_SECRET = os.environ.get("COGNITO_CLIENT_SECRET", config.get('CognitoClientSecret'))
REDIRECT_URI = os.environ.get("REDIRECT_URI", config.get('RedirectUri'))
HOSTEDUIPATH = os.environ.get("HOSTEDUIPATH", config.get('HostedUiPath'))

def get_config():
    if any([not COGNITO_CLIENT_ID, not COGNITO_CLIENT_SECRET, not REDIRECT_URI, not HOSTEDUIPATH]):
        raise ValueError("""
            Missing required ENV VARs:
                * COGNITO_CLIENT_ID
                * COGNITO_CLIENT_SECRET
                * REDIRECT_URI
                * HOSTEDUIPATH
            """
        )

    return {
        "COGNITO_CLIENT_ID": COGNITO_CLIENT_ID,
        "COGNITO_CLIENT_SECRET": COGNITO_CLIENT_SECRET,
        "REDIRECT_URI": REDIRECT_URI,
        "HOSTEDUIPATH": HOSTEDUIPATH,
    }

config = get_config()
