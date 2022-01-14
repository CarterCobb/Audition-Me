import json
import os
import boto3
from base64 import b64decode, b64encode
from json import loads
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
    try:
        user = get_user(event["headers"]["Authorization"])
        print(user)
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
                req_body = event["body"]
                if (event["isBase64Encoded"]):
                    req_body = b64decode(req_body)
                req_body = loads(req_body)
                id = uniqueid()
                req_body["id"] = id
                table = dynamodb.Table("performance")
                table.put_item(Item=req_body)
                # Add performance to user list
                table_user = dynamodb.Table("users")
                table_user.update_item(
                    Key={"id": user["id"]},
                    UpdateExpression="set performances = list_append(if_not_exists(performances, :empty_list), :performance)",
                    ExpressionAttributeValues={
                        ':empty_list': [],
                        ':performance': [id],
                    },
                    ReturnValues="UPDATED_NEW")
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
                        return {"statusCode": 204}
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
            if user["permissions"]["can_delete_performance"]:
                if "id" in event["queryStringParameters"]:
                    id = event["queryStringParameters"]["id"]
                    if id in user["performances"]:
                        # Delete performance
                        table = dynamodb.Table("performance")
                        table.delete_item(Key={"id": id})
                        # Remove referance to performance on user
                        table_user = dynamodb.Table("users")
                        new_performance_list = user["performances"].remove(id)
                        table_user.update_item(
                            Key={"id": user["id"]},
                            UpdateExpression="set performances = :performances",
                            ExpressionAttributeValues={
                                ':performances': new_performance_list if new_performance_list != None else [],
                            }, ReturnValues="UPDATED_NEW")
                        return {"statusCode": 204}
                    else:
                        return {
                            "statusCode": 403,
                            "error": "UNOWNED_PERFORMANCE_ACTION",
                            "message": "Unable to perform action on performance becasue you do not own it."
                        }
                else:
                    return {
                        "statusCode": 400,
                        "error": "NO_ID",
                        "message": "`id` is a required query parameter"
                    }
        return {
            "statusCode": 404,
            "error": "ACTION_NOT_FOUND",
            "message": "The requested action cannot be found for the authenticated user."
        }
    except:
        return {
            "statusCode": 500,
            "error": "UNKNOWN_ERROR",
            "message": "An unknown error occured"
        }


def get_user(token):
    """
    Get the full representation of an authenticated user.
    Also sets the users permissions from their security group.
    """
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
    """
    Find the security group for the user.
    """
    table = dynamodb.Table("security_group")
    group = table.get_item(Key={"id": user["security_group"]})
    if not "Item" in group:
        return None
    return group["Item"]


def get_permissions(ids):
    """
    Get the permission metadata for each given id
    """
    permissions = {
        "can_post_performance": False,
        "can_delete_performance": False,
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


def uniqueid():
    """
    Generate a new if for the performance
    """
    return b64encode(os.urandom(16)).decode('ascii')


# TESTING

performer_token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpZCI6IjYxZTA2OTc0N2M4ZjExOTg2ZjgwZmVhMSJ9.AFxp8Sd6jJ3LPXdv_RhAxAbPFYyVDgV7x9G5wRDZ-90"
director_token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpZCI6IjYxZTFiZTFhNTYzNzdlODhiNWFhYzhhOSJ9.vaiQSCAwBNedjYPTny1TAMX5fTvUVtF7E5ck8Y6sBhk"

data = {"headers": {
    "Authorization": director_token},
    "httpMethod": "DELETE",
    "queryStringParameters": {
    "action_type": "cast",
    "id": "Mx/ULXF2tPst7D07iLvlog=="
},
    "body": "ewogICAgInRpdGxlIjogImZpcnN0IHBlcmZvcm1hbmNlIiwKICAgICJkaXJlY3RvciI6ICI2MWUxYmUxYTU2Mzc3ZTg4YjVhYWM4YTkiLAogICAgImNhc3RpbmdfZGlyZWN0b3IiOiAiNjFlMWJlMWE1NjM3N2U4OGI1YWFjOGE5IiwKICAgICJsaXZlX3BlcmZvcm1hbmNlX2RhdGVzIjogWyIyMDIyLTAxLTE0IDExOjM2OjUxLjc4OTI1MyIsICIyMDIyLTAxLTE0IDExOjM3OjAzLjkyODk0NyJdLAogICAgImNhc3QiOiBbIjYxZTA2OTc0N2M4ZjExOTg2ZjgwZmVhMSJdLAogICAgImF1ZGl0aW9ucyI6IFsiNjFlMDY5NzQ3YzhmMTE5ODZmODBmZWExIl0sCiAgICAidmVudWUiOiAiMTIzIE1pZG8gTm93aGVyZSBMYW5lIgp9",
    "isBase64Encoded": True
}

{
    "title": "first performance",
    "director": "61e1be1a56377e88b5aac8a9",
    "casting_director": "61e1be1a56377e88b5aac8a9",
    "live_performance_dates": ["2022-01-14 11:36:51.789253", "2022-01-14 11:37:03.928947"],
    "cast": ["61e069747c8f11986f80fea1"],
    "auditions": ["61e069747c8f11986f80fea1"],
    "venue": "123 Mido Nowhere Lane"
}
# d = datetime.datetime.fromisoformat("2022-01-14 11:37:03.928947")

print(lambda_handler(data, None))
