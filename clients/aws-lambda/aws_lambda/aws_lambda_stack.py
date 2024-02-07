from aws_cdk import (
    aws_cognito,
    aws_lambda,
    aws_apigatewayv2,
    aws_apigatewayv2_integrations,
    aws_apigatewayv2_authorizers,
    Arn,
    CfnOutput,
    Stack,
)
from constructs import Construct

class AwsLambdaStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, user_pool_id: str, user_pool_client_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Import the userpool from the already deployed stack
        user_pool_arn = Arn.format(
            stack=self,
            components={
                "service": "cognito-idp",
                "resource": "userpool",
                "resourceName": user_pool_id,
            },
        )
        user_pool = aws_cognito.UserPool.from_user_pool_arn(
            self, "UserPool", user_pool_arn,
        )

        user_pool_client = aws_cognito.UserPoolClient.from_user_pool_client_id(
            self, "UserPoolClient", user_pool_client_id,
        )

        # Create an authorizer for the private route
        # https://docs.aws.amazon.com/apigateway/latest/developerguide/apigateway-integrate-with-cognito.html
        authorizer = aws_apigatewayv2_authorizers.HttpUserPoolAuthorizer(
            "Authorizer",
            user_pool,
            user_pool_clients=[user_pool_client],
        )

        # Create an HTTP API
        api = aws_apigatewayv2.HttpApi(self, "HttpApi")
        CfnOutput(self, "ApiUrl", value=api.url)

        # Create a lambda function to manage the Private route
        private_fn = aws_lambda.Function(
            self, "PrivateFunction",
            handler="main.private_handler",
            runtime=aws_lambda.Runtime.PYTHON_3_12,
            code=aws_lambda.Code.from_asset("lambdas"),
        )

        private_fn_integration = aws_apigatewayv2_integrations.HttpLambdaIntegration(
            "PrivateFnIntegration", private_fn
        )

        api.add_routes(
            path="/private",
            methods=[aws_apigatewayv2.HttpMethod.GET],
            authorizer=authorizer,
            integration=private_fn_integration,
        )

        # Create a lambda function to manage the Public route
        public_fn = aws_lambda.Function(
            self, "PublicFunction",
            handler="main.public_handler",
            runtime=aws_lambda.Runtime.PYTHON_3_12,
            code=aws_lambda.Code.from_asset("lambdas"),
        )

        public_fn_integration = aws_apigatewayv2_integrations.HttpLambdaIntegration(
            "PublicFnIntegration", public_fn
        )

        api.add_routes(
            path="/public",
            methods=[aws_apigatewayv2.HttpMethod.GET],
            integration=public_fn_integration,
        )
