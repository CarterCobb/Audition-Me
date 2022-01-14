from ast import NotIn
import json
import os
import boto3
from base64 import b64decode
from json import loads, dumps
from bcrypt import checkpw
from jwt import decode

# JWT_SECRET = os.environ["SECRET"]
JWT_SECRET = "rtINZYEEUWkHJ8gmCDyQyfqDZVAROUttk99e9MIpHDc97KbUeduDngegXMhj5BAG6dKlSmr9k5uGaiQh"
dynamodb = boto3.resource("dynamodb")


def lambda_handler(event, context):
    """
    Perfoms all the actions for a perfomace. 
    Uses http methods to determine what actions to take vs creating a new
    lambda for each action.
    """
    user = get_user(event["headers"]["Authorization"])
    if event["httpMethod"] == "GET":
        # Search for performance
        if user["permissions"]["can_search_performances"]:
            # Search
            return {
                "statusCode": 200,
                "performances": []
            }
    elif event["httpMethod"] == "POST":
        if user["permissions"]["can_post_performance"]:
            # Create performace from body
            return {"statusCode": 201}
    elif event["httpMethod"] == "PUT":
        # Audition or cast a perfomer
        if "action_type" in event["queryStringParameters"]:
            if event["queryStringParameters"]["action_type"] == "audition":
                if user["permissions"]["can_audition"]:
                    # Sign performer up to the perfomance
                    # Perfomrer only
                    #  (add user id to the `auditions` list)
                    return {
                        "statusCode": 200,
                        "message": "auditioned"
                    }
            elif event["queryStringParameters"]["action_type"] == "cast":
                if user["permissions"]["can_cast_performer"]:
                    # cast performer to this performance
                    # Director only
                    #  (add user id to the `cast` list)
                    return {
                        "statusCode": 200,
                        "message": "casted"
                    }
            else:
                return {
                    "statusCode": 404,
                    "error": "UNKNOW_ACTION_TYPE",
                    "message": "the `action_type` provided is invalid"
                }
        else:
            return {
                "statusCode": 400,
                "error": "NO_ACTION_TYPE",
                "message": "`action_type` query param is required"
            }
    elif event["httpMethod"] == "DELETE":
        if user["permissions"]["can_delete_performace"]:
            # Delete perfomance
            return {"statusCode": 204}
    return {
        "error": "ACTION_NOT_FOUND",
        "message": "The requested action cannot be found for the authenticated user.",
        "code": 404
    }


def get_user(token):
    table = dynamodb.Table("users")
    payload = decode(token, JWT_SECRET, algorithms=["HS256"])
    user = table.get_item(Key={"id": payload["id"]})
    if not "Item" in user:
        return None
    security_group = get_security_group(user["Item"])
    user["Item"]["security_group"] = security_group
    user["Item"]["permissions"] = get_permissions(
        security_group["permissions"])
    return user["Item"]


def get_security_group(user):
    table = dynamodb.Table("security_group")
    group = table.get_item(Key={"id": user["security_group"]})
    if not "Item" in group:
        return None
    return group["Item"]


def get_permissions(ids):
    permissions = {
        "can_post_performance": False,
        "can_delete_performace": False,
        "can_cast_performer": False,
        "can_search_performances": False,
        "can_audition": False,
        "is_performer": False
    }
    table = dynamodb.Table("permission")
    for permission_id in ids:
        permission = table.get_item(Key={"id": permission_id})
        if "Item" in permission:
            permissions[permission["Item"]["descriptor"].lower()] = json.loads(
                permission["Item"]["metadata"])[permission["Item"]["descriptor"].lower()]
    return permissions


# TESTING
data = {"headers":
        {"Authorization": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpZCI6IjYxZTA2OTc0N2M4ZjExOTg2ZjgwZmVhMSJ9.AFxp8Sd6jJ3LPXdv_RhAxAbPFYyVDgV7x9G5wRDZ-90"},
        "httpMethod": "GET"}
print(lambda_handler(data, None))
