import os
import boto3
from jwt import decode, encode
import jwt

JWT_SECRET = "12121212"  # os.environ["SECRET"]
dynamodb = boto3.resource("dynamodb")


def lambda_handler(event, context):
    try:
        auth_token = event["headers"]["Authorization"]
        payload = decode(auth_token, JWT_SECRET, algorithms=["HS256"])
        table = dynamodb.Table("users")
        user = table.get_item(Key={"id": payload["id"]})
        if not("Item" in user):
            return {
                "statusCode": 404,
                "error": "USER_NOT_FOUND",
                "message": "User does not exist"
            }
    except KeyError:
        return {
            "statusCode": 400,
            "error": "NO_AUTH_TOKEN",
            "message": "Failed to authentice"
        }
    except jwt.exceptions.DecodeError:
        return {
            "statusCode": 500,
            "error": "DECODE_ERROR",
            "message": "Failed to decode token"
        }
    except:
        return {
            "statusCode": 500,
            "error": "UNKNOWN_ERORR",
            "message": "An unknown error occured"
        }
    return {"statusCode": 200, "user": user["Item"]}

# TESTING 
auth = encode({"id": "asdsad3q4324"}, JWT_SECRET, algorithm="HS256")
print(auth)

lambda_ = lambda_handler({"headers": {"Authorization": auth}}, None)
print(lambda_)
