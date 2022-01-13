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
    user = get_user(event["headers"]["Authorization"])
    return user


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
data = {"headers": {"Authorization": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpZCI6IjYxZTA2OTc0N2M4ZjExOTg2ZjgwZmVhMSJ9.AFxp8Sd6jJ3LPXdv_RhAxAbPFYyVDgV7x9G5wRDZ-90"}}
print(lambda_handler(data, None))
