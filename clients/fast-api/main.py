from typing import Annotated
import time

import boto3
import jwt
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from pydantic import BaseModel

from config import config

cognito_client = boto3.client('cognito-idp')

TOKEN_DELIMITER = "++++++"

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str

    @classmethod
    def from_cognito(cls, resp):
        """Create a Token from the response from Cognito."""
        access_token = resp['AuthenticationResult']['AccessToken']
        id_token = resp['AuthenticationResult']['IdToken']

        # The "access_token" and "id_token" are joined together with a delimiter
        # so that we can pass them around as a single string.
        token_data = TOKEN_DELIMITER.join([access_token, id_token])
        
        # The refresh token is separate and returned in the call to
        # initiate_auth. We store it separately in the fronr-end client
        # and using it to get a new access token when the current one expires
        # is left as an exercise for the reader.
        refresh_token = resp['AuthenticationResult']['RefreshToken']

        return cls(
            access_token=token_data,
            refresh_token=refresh_token,
            token_type=resp['AuthenticationResult']['TokenType']
        )


class User(BaseModel):
    username: str
    email: str
    disabled: bool = False


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

app = FastAPI()


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        access_token = token.split(TOKEN_DELIMITER)[0]
        access_payload = jwt.decode(access_token, options={"verify_signature": False})

        if access_payload.get("exp") < int(time.time()):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Expired token",
                headers={"WWW-Authenticate": "Bearer"},
            )

        username: str = access_payload.get("sub")
    except jwt.exceptions.DecodeError:
        raise credentials_exception
    
    id_token = token.split(TOKEN_DELIMITER)[1]
    id_payload = jwt.decode(id_token, options={"verify_signature": False})
    user = User(
        username=username,
        email=id_payload.get("email"),
    )
    return user


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)]
):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


@app.post("/token")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
) -> Token:

    def secret_hash(username):
        """ Create a secret hash for cognito
        See https://docs.aws.amazon.com/cognito/latest/developerguide/signing-up-users-in-your-app.html#cognito-user-pools-computing-secret-hash
        """

        import hmac
        import hashlib
        import base64

        message = bytes(username + config['COGNITO_CLIENT_ID'],'utf-8') 
        key = bytes(config['COGNITO_CLIENT_SECRET'],'utf-8')
        secret_hash = base64.b64encode(hmac.new(key, message, digestmod=hashlib.sha256).digest()).decode() 
        return secret_hash

    resp = cognito_client.initiate_auth(
        ClientId=config['COGNITO_CLIENT_ID'],
        AuthFlow='USER_PASSWORD_AUTH',
        AuthParameters={
            'USERNAME': form_data.username,
            'PASSWORD': form_data.password,
            'SECRET_HASH': secret_hash(form_data.username)
        }
    )
    return Token.from_cognito(resp)


@app.get("/users/me/", response_model=User)
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_active_user)]
):
    return current_user
