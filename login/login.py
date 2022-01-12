import os
import boto3
from jwt import decode

JWT_SECRET = os.environ["SECRET"]
dynamodb = boto3.resource("dynamodb")


def lambda_handler(event, context):
    try:
        auth_token = event["body"]["Authorization"]
        payload = decode(auth_token, JWT_SECRET, algorithms=["HS256"])
        table = dynamodb.Table("Users")
        table.get_item(Key={"id": payload["id"]})
    except KeyError:
        return {
            "error": "NO_AUTH_HEADER",
            "code": 400
        }
    return ""
