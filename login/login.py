import os
import boto3
import base64
import json

dynamodb = boto3.resource("dynamodb")


def lambda_handler(event, context):
    try:
        req_body = event["body"]
        if (event["isBase64Encoded"]):
            req_body = base64.b64decode(req_body)
        body_obj = json.loads(req_body)
        table = dynamodb.Table("Users")
        table.get_item(Key={"email": body_obj["email"]})
        # Verify the user exists then:
        # Need to use bcrypt to verify password then:
        # return correct response back to caller
    except KeyError:
        return {
            "error": "NO_AUTH_HEADER",
            "code": 400
        }
    return ""
