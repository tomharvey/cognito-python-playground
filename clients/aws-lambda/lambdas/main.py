import json

def private_handler(event, context):
    return _json_response({"message": "Hello, Authorized World!"})


def public_handler(event, context):
    return _json_response({"message": "Hello, World!"})

def _json_response(body):
    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json",
        },
        "body": json.dumps(body)
    }
