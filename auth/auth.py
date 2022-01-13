import os
import boto3
from jwt import decode, DecodeError

# JWT_SECRET = os.environ["SECRET"]
JWT_SECRET = "rtINZYEEUWkHJ8gmCDyQyfqDZVAROUttk99e9MIpHDc97KbUeduDngegXMhj5BAG6dKlSmr9k5uGaiQh"
dynamodb = boto3.resource("dynamodb")


def lambda_handler(event, context):
    """
    Authorizes the user and returns applicable user authorization status.
    """
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
    except DecodeError:
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
data = {"headers": {"Authorization": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpZCI6IjYxZTA2OTc0N2M4ZjExOTg2ZjgwZmVhMSJ9.AFxp8Sd6jJ3LPXdv_RhAxAbPFYyVDgV7x9G5wRDZ-90"}, "isBase64Encoded": False}

print(lambda_handler(data, None))
