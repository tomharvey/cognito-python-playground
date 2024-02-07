

def private_handler(event, context):
    return {
        "statusCode": 200,
        "body": "Hello, Authenticated User!"
    }


def public_handler(event, context):
    return {
        "statusCode": 200,
        "body": "Hello, World!"
    }
