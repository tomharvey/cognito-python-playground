#!/usr/bin/env python3
import aws_cdk as cdk

from cognito_playground.cognito_playground_stack import CognitoPlaygroundStack


app = cdk.App()
CognitoPlaygroundStack(app, "CognitoPlaygroundStack",
    domain_prefix="tom-playground",
)

app.synth()
