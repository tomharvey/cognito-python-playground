from aws_cdk import (
    aws_cognito,
    custom_resources,
    RemovalPolicy,
    Stack,
    CfnOutput,
)
from constructs import Construct

class CognitoPlaygroundStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, domain_prefix: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        user_pool = aws_cognito.UserPool(self, "CognitoUserPool",
            self_sign_up_enabled=True,
            sign_in_case_sensitive=False,
            sign_in_aliases=aws_cognito.SignInAliases(email=True),
            auto_verify=aws_cognito.AutoVerifiedAttrs(email=True),
            user_verification=aws_cognito.UserVerificationConfig(
                email_style=aws_cognito.VerificationEmailStyle.LINK,
                email_subject="Verify your email for our awesome app!",
                email_body="You have been invited to join our awesome app! {##Verify Email##}",
            ),
            removal_policy=RemovalPolicy.DESTROY,
        )
        CfnOutput(self, "UserPoolId", value=user_pool.user_pool_id)

        # We require a custom domain to be able to use the hosted UI
        domain = user_pool.add_domain("CognitoDomain", cognito_domain=aws_cognito.CognitoDomainOptions(
            domain_prefix=domain_prefix,
        ))
        domain.apply_removal_policy(RemovalPolicy.DESTROY)
        CfnOutput(self, "HostedUiPath",
            value=f"https://{domain.domain_name}.auth.{self.region}.amazoncognito.com",
        )

        # The app client interacts between our user pool and web/mobile app
        # It is used to configure the hosted UI
        CALLBACK_URL = "http://localhost:3000/callbacks/cognito/login"
        client = user_pool.add_client("CognitoUserPoolClient",
            generate_secret=True,
            prevent_user_existence_errors=True,
            supported_identity_providers=[aws_cognito.UserPoolClientIdentityProvider.COGNITO],
            auth_flows=aws_cognito.AuthFlow(
                user_password=True,
            ),
            o_auth=aws_cognito.OAuthSettings(
                callback_urls=[CALLBACK_URL],
            ),
        )
        client.apply_removal_policy(RemovalPolicy.DESTROY)
        CfnOutput(self, "RedirectUri", value=CALLBACK_URL)
        CfnOutput(self, 'CognitoClientId', value=client.user_pool_client_id)
        # The below is a secruity risk and should not be done in a real application
        # it's purely for the purpose of this demo to make access to the secret value easier.
        # In a real application, you would use a more secure way to communicate the client secret.
        CfnOutput(self, 'CognitoClientSecret', value=client.user_pool_client_secret.unsafe_unwrap())

        # Create an initial user
        INITIAL_USER_EMAIL = "user@example.com"
        INITIAL_USER_PASSWORD = "Password123!"
        CfnOutput(self, "LoginUsername", value=INITIAL_USER_EMAIL)
        CfnOutput(self, "LoginPassword", value=INITIAL_USER_PASSWORD)

        create_user = custom_resources.AwsCustomResource(self, "CreateUser",
            policy=custom_resources.AwsCustomResourcePolicy.from_sdk_calls(
                resources=custom_resources.AwsCustomResourcePolicy.ANY_RESOURCE,
            ),
            on_create=custom_resources.AwsSdkCall(
                service="CognitoIdentityServiceProvider",
                action="adminCreateUser",
                parameters={
                    "UserPoolId": user_pool.user_pool_id,
                    "Username": INITIAL_USER_EMAIL,
                    "TemporaryPassword": INITIAL_USER_PASSWORD,
                    "UserAttributes": [
                        {"Name": "email", "Value": INITIAL_USER_EMAIL},
                        {"Name": "email_verified", "Value": "true"},
                    ],
                },
                physical_resource_id=custom_resources.PhysicalResourceId.of("CreateUser"),
            ),
        )
        create_user.node.add_dependency(user_pool)

        # Confirm the user's password so you don't need to change it on first login
        # You would not want to do this in a real application
        # it's purely for the purpose of this demo to make logging in easier
        confirm_user_password = custom_resources.AwsCustomResource(self, "ConfirmUserPassword",
            policy=custom_resources.AwsCustomResourcePolicy.from_sdk_calls(
                resources=custom_resources.AwsCustomResourcePolicy.ANY_RESOURCE,
            ),
            on_create=custom_resources.AwsSdkCall(
                service="CognitoIdentityServiceProvider",
                action="adminSetUserPassword",
                parameters={
                    "UserPoolId": user_pool.user_pool_id,
                    "Username": INITIAL_USER_EMAIL,
                    "Password": INITIAL_USER_PASSWORD,
                    "Permanent": True,
                },
                physical_resource_id=custom_resources.PhysicalResourceId.of("ConfirmUser"),
            ),
        )
        confirm_user_password.node.add_dependency(create_user)
