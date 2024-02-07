from flask import (
    Flask,
    redirect,
    request,
    session,
)

from auth_handlers import (
    cognito_login_path,
    exchange_auth_code_for_tokens,
    exchange_refresh_token_for_tokens,
    token_is_valid,
)


app = Flask(__name__)
app.secret_key = "ThisIsSuperSecret"


@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

@app.route("/login")
def login():
    """Redirect to the Cognito hosted UI
    """
    return redirect(cognito_login_path)

@app.route('/callbacks/cognito/login', methods=['GET'])
def callback():
    """Exchange the Authorization Code for a JWT token
    """
    code = request.args.get('code')

    # Exchange the code for tokens
    id_token, access_token, refresh_token = exchange_auth_code_for_tokens(code)

    # Validate the token for authenticity and expiration
    if not token_is_valid(id_token):
        return "<p>Expired token</p>", 401

    # If we successfully get the tokens, we store them in the session
    session["id_token"] = id_token
    session["access_token"] = access_token
    session["refresh_token"] = refresh_token

    return "<p>Success. Go to <a href='/private'>the private area</a></p>"

@app.route("/private")
def private():
    """Show the private area - if you're logged in
    """
    id_token = session.get("id_token")

    # If there is no token, you've never logged in.
    if not id_token:
        return "<p>Not logged in. <a href='/login'>Login in here.</a></p>", 401

    # If it has expired, we can use the refresh token to get a new one
    if not token_is_valid(id_token):
        refresh_token = session["refresh_token"]
        id_token, access_token = exchange_refresh_token_for_tokens(refresh_token)

        # If we fail to refresh it, we need to log in again
        if not token_is_valid(id_token):
            return "<p>Expired token. <a href='/login'>Login in again here.</a></p>", 401
        
        print("Token refreshed")  # So you can see in the console that it's working

        session["id_token"] = id_token
        session["access_token"] = access_token

    return "<p>Welcome to the secret space!</p>"

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=3000)
