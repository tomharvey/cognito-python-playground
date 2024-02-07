# Flask client

This is a basic flask app.

It starts from the hello world example and adds a few more routes
to demonstrate how to use the Cognito Hosted UI for authentication.

There is one public endpoint, and one private endpoint (which requires
you be an authenticated user).

It also has endpoints to start, and handle the completion of, the login flow.

## Running the app

### Setup
You will need some configuration to tell the app abount the Cognito
Userpool it should use for auth.

You can copy the cdk_outputs.json file from the CDK deployment to this folder.

Or, see the config.py to see what ENV VARS you need to set.

### Dependencies

You can (and should) create a venv for this app:

```bash
    python -m venv .flask-client-venv
```

And then activate it:

```bash
    source .flask-client-venv/bin/activate
```

You will then need to install the dependencies with:

```bash
    pip install -r requirements.txt
```

Then, you can run the app with:

```bash
    python hello.py
``` 

And visit http://localhost:3000 in your browser.

## Routes

- `/` - welcomes everyone and anyone to the app
- `/private` - only show its contents if you're logged in
- `/login` - takes you to the Cognito Hosted UI to start the login flow
- `/callbacks/cognito/login` - the callback URL for the Cognito Hosted UI

Once you complete the login flow, you will come back to the `/callbacks/cognito/login` route,
and should then be able to access the `/private` route.

If your token expires when refreshing the `/private` route, the app will attempt to refresh the token

If you're not logged in, you will see a message directing you to the `/login` route to start the login flow again.
