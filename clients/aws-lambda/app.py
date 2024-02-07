#!/usr/bin/env python3
import os

import aws_cdk as cdk

from aws_lambda.aws_lambda_stack import AwsLambdaStack


app = cdk.App()
AwsLambdaStack(app, "AwsLambdaStack",
    user_pool_id="us-east-1_rjf4huGs2",
    env=cdk.Environment(account=os.getenv('CDK_DEFAULT_ACCOUNT'), region=os.getenv('CDK_DEFAULT_REGION')),
)

app.synth()
