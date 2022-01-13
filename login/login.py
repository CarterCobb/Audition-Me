import os
import boto3
from base64 import b64decode
from json import loads, dumps
from bcrypt import checkpw
from jwt import encode

# JWT_SECRET = os.environ["SECRET"]
JWT_SECRET = "rtINZYEEUWkHJ8gmCDyQyfqDZVAROUttk99e9MIpHDc97KbUeduDngegXMhj5BAG6dKlSmr9k5uGaiQh"
dynamodb = boto3.resource("dynamodb")


def lambda_handler(event, context):
    """
    Takes in the email and apssword from the body and if its valid will return an access token.
    """
    try:
        req_body = event["body"]
        if ("isBase64Encoded" in event and event["isBase64Encoded"]):
            req_body = b64decode(req_body)
        body_obj = loads(req_body)
        table = dynamodb.Table("users")
        response = table.scan()
        result = response['Items']
        while 'LastEvaluatedKey' in response:
            response = table.scan(
                ExclusiveStartKey=response['LastEvaluatedKey'])
            result.extend(response['Items'])
        for item in result:
            if "email" in body_obj and (body_obj["email"] == item["email"]):
                if("password" in body_obj and checkpw(str.encode(body_obj["password"]), str.encode(item["password"]))):
                    return {
                        "statusCode": 200,
                        "accessToken": encode({"id": item["id"]}, JWT_SECRET, algorithm="HS256"),
                    }
        return {
            "statusCode": 404,
            "error": "USER_NOT_FOUND",
            "message": "Failed to login"
        }
    except:
        return {
            "ststusCode": 500,
            "error": "UNKNOWN_ERROR",
            "message": "An unknown error occoured"
        }


# TESTING
data = {"body": dumps({"email": "carter.cobb72@gmail.com",
                      "password": "12345"}), "isBase64Encoded": False}

print(lambda_handler(data, None))
