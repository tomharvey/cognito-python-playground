



 uvicorn main:app --reload --port 3001


 # https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/


For refresh and/or ID token inclusion - look at the following link, or extend OAuth2PasswordBearer to include multiple tokens.
# https://indominusbyte.github.io/fastapi-jwt-auth/usage/refresh/

https://docs.aws.amazon.com/cognito/latest/developerguide/amazon-cognito-user-pools-using-the-id-token.html
https://docs.aws.amazon.com/cognito/latest/developerguide/amazon-cognito-user-pools-using-the-access-token.html




# Fast API with Cognito

This is based on the OAuth2 JWT example from the the
[FastAPI documentation](https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/).

It edits the mechanism within the `login_for_access_token` function
to get a JWT from AWS Cognito, instead of generating a JWT itself after
verifying the username and password in a `fake_users_db`.

It's otherwise largely unchanged from the original example, but I have removed some
functions which are no longer required - such as `fake_hash_password` and JWT creation.

There is a login endpoint and one private endpoint, which requires a valid JWT to access.

As this is FastAPI, there is an OpenAPI schema available at `/docs` which you can use to
interact with the app.

## Running the app

### Setup
You will need some configuration to tell the app abount the Cognito
Userpool it should use for auth.

You can copy the cdk_outputs.json file from the CDK deployment to this folder.

Or, see the config.py to see what ENV VARS you need to set.

### Dependencies

You can (and should) create a venv for this app:

```bash
    python -m venv .fastapi-client-venv
```

And then activate it:

```bash
    source .fastapi-client-venv/bin/activate
```

You will then need to install the dependencies with:

```bash
    pip install -r requirements.txt
```

Then, you can run the app with:

```bash
    uvicorn main:app --reload 
``` 

And visit http://localhost:8000/docs in your browser to see the OpenAPI docs.

You can use the "Authorize" button at the top of the docs to log in with Cognito:
Username: `user@example.com`
Password: `Password123!`

Then use the "Try it out" button to make requests to the `/users/me/` endpoint.

## Routes

- `/login` - accepts a username and password and returns a JWT
- `/users/me/` - requires a JWT and returns your user infomration

Once you complete the login flow, you will come back to the `/callbacks/cognito/login` route,

You should see a 401 response if you try to access `/users/me/` without a valid JWT.

I've not implemented any refresh_token use here, but you can see the refresh_token in
the response from the `/login` endpoint. Your API client can store that and use it when it's required.
