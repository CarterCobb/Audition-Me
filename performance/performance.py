import json
import os
import boto3
from base64 import b64decode, b64encode
from json import loads, dumps
from jwt import decode
from requests import post

JWT_SECRET = os.environ["SECRET"]
# JWT_SECRET = "rtINZYEEUWkHJ8gmCDyQyfqDZVAROUttk99e9MIpHDc97KbUeduDngegXMhj5BAG6dKlSmr9k5uGaiQh"
dynamodb = boto3.resource("dynamodb")


def lambda_handler(event, context):
    """
    Perfoms all the actions for a perfomace. 
    Uses http methods to determine what actions to take vs creating a new
    lambda for each action.
    """
    try:
        AUTH_TOKEN = event["headers"]["Authorization"]
        user = get_user(AUTH_TOKEN)
        if event["httpMethod"] == "GET":
            # Search for performance
            if user["permissions"]["can_search_performances"]:
                # Search
                filter = None
                if "filter" in event["queryStringParameters"]:
                    filter = event["queryStringParameters"]["filter"]
                # Get all performances
                table = dynamodb.Table("performance")
                response = table.scan()
                result = response["Items"]
                while "LastEvaluatedKey" in response:
                    response = table.scan(
                        ExclusiveStartKey=response["LastEvaluatedKey"])
                    result.extend(response["Items"])
                # Apply filter if any; its an optional query string param
                filtered_result = []
                if filter != None:
                    for performance in result:
                        if filter in dumps(performance):
                            filtered_result.append(performance)
                return {
                    "statusCode": 200,
                    "performances": result if filter == None else filtered_result
                }
        elif event["httpMethod"] == "POST":
            if user["permissions"]["can_post_performance"]:
                # Create performace from body
                req_body = event["body"]
                if ("isBase64Encoded" in event and event["isBase64Encoded"]):
                    req_body = loads(b64decode(req_body))
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
                        ":empty_list": [],
                        ":performance": [id],
                    },
                    ReturnValues="UPDATED_NEW")
                return {"statusCode": 201}
        elif event["httpMethod"] == "PUT":
            # Audition or cast a perfomer
            if "action_type" in event["queryStringParameters"]:
                if event["queryStringParameters"]["action_type"] == "audition":
                    if user["permissions"]["can_audition"]:
                        if "performance" in event["queryStringParameters"]:
                            # Add user id to the auditions list on the performance
                            table = dynamodb.Table("performance")
                            table.update_item(
                                Key={
                                    "id": event["queryStringParameters"]["performance"]},
                                UpdateExpression="set auditions = list_append(if_not_exists(auditions, :empty_list), :user)",
                                ExpressionAttributeValues={
                                    ":empty_list": [],
                                    ":user": [user["id"]],
                                },
                                ReturnValues="UPDATED_NEW"
                            )
                            try:
                                p = table.get_item(
                                    Key={"id": event["queryStringParameters"]["performance"]})
                                if ("Item" in p):
                                    director = p["Item"]["casting_director"]
                                    if(director):
                                        _performer = user["id"]
                                        _performance = event["queryStringParameters"]["performance"]
                                        user_table = dynamodb.Table("users")
                                        director_full = user_table.get_item(
                                            Key={"id": director})
                                        if("Item" in director_full):
                                            send_email(
                                                director_full["Item"]["email"], "New Audition", f"Performer id: {_performer} has auditioned for performance id: {_performance}", AUTH_TOKEN)
                            except:
                                print("Exception occurred", exc_info=True)
                            finally:
                                return {"statusCode": 204}
                        else:
                            return {
                                "statusCode": 400,
                                "error": "MISSING_PERFOMANCE",
                                "message": "`performance` is a requried query parameter"
                            }
                elif event["queryStringParameters"]["action_type"] == "cast":
                    # // TODO: Schedule email for the performer for 7pm the evening before each performace time
                    if user["permissions"]["can_cast_performer"]:
                        if "performer" in event["queryStringParameters"]:
                            # Safe to get performer id
                            performer = event["queryStringParameters"]["performer"]
                            if "performance" in event["queryStringParameters"]:
                                # Safe to get performance id
                                performance = event["queryStringParameters"]["performance"]
                                if performance in user["performances"]:
                                    # Add perfromer id to casted_performers list on then performance
                                    table = dynamodb.Table("performance")
                                    table.update_item(
                                        Key={"id": performance},
                                        UpdateExpression="set casted_performers = list_append(if_not_exists(casted_performers, :empty_list), :performer)",
                                        ExpressionAttributeValues={
                                            ":empty_list": [],
                                            ":performer": [performer],
                                        },
                                        ReturnValues="UPDATED_NEW"
                                    )
                                    # Add the performance to the performers `participating_in` list
                                    table_user = dynamodb.Table("users")
                                    table_user.update_item(
                                        Key={"id": performer},
                                        UpdateExpression="set participating_in = list_append(if_not_exists(participating_in, :empty_list), :performance)",
                                        ExpressionAttributeValues={
                                            ":empty_list": [],
                                            ":performance": [performance],
                                        },
                                        ReturnValues="UPDATED_NEW"
                                    )
                                    try:
                                        p = table_user.get_item(
                                            Key={"id": performer})
                                        if ("Item" in p):
                                            email = p["Item"]["email"]
                                            if(email):
                                                send_email(
                                                    email, "New Audition", f"You have been cast for perfromance id: {performance}! Congradulations!!!", AUTH_TOKEN)
                                    except:
                                        print("Exception occurred",
                                              exc_info=True)
                                    finally:
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
                                    "error": "UNKNOWN_PERFORMANCE",
                                    "message": "`performance` is a required query string parameter"
                                }
                        else:
                            return {
                                "statusCode": 400,
                                "error": "UNKNOWN_PERFORMER",
                                "message": "`performer` is a required query string parameter"
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
                                ":performances": new_performance_list if new_performance_list != None else [],
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
    except Exception as e:
        return {
            "statusCode": 500,
            "error": "UNKNOWN_ERROR",
            "message": "An unknown error occured",
            "exception": str(e)
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
    return b64encode(os.urandom(16)).decode("ascii").replace("=", "")


def send_email(to, subject, message, auth):
    URL = "https://wlzehlqpta.execute-api.us-west-1.amazonaws.com/beta/email"
    BODY = {"to": to, "subject": subject, "message": message}
    HEADERS = {
        "Content-Type": "application/json",
        "Authorization": auth}
    post(url=URL, data=dumps(BODY), headers=HEADERS)


# TESTING

performer_token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpZCI6IjYxZTA2OTc0N2M4ZjExOTg2ZjgwZmVhMSJ9.AFxp8Sd6jJ3LPXdv_RhAxAbPFYyVDgV7x9G5wRDZ-90"
director_token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpZCI6IjYxZTFiZTFhNTYzNzdlODhiNWFhYzhhOSJ9.vaiQSCAwBNedjYPTny1TAMX5fTvUVtF7E5ck8Y6sBhk"

data = {"headers": {
    "Authorization": director_token},
    "httpMethod": "PUT",
    "queryStringParameters": {
        "action_type": "cast",  # cast | audition
        "id": "Mx/ULXF2tPst7D07iLvlog==",
        "performer": "61e069747c8f11986f80fea1",
        "performance": "KHBsdf234fsdkhg234",
        "filter": "I love pie"
},
    "body": "ewogICAgInRpdGxlIjogImZpcnN0IHBlcmZvcm1hbmNlIiwKICAgICJkaXJlY3RvciI6ICI2MWUxYmUxYTU2Mzc3ZTg4YjVhYWM4YTkiLAogICAgImNhc3RpbmdfZGlyZWN0b3IiOiAiNjFlMWJlMWE1NjM3N2U4OGI1YWFjOGE5IiwKICAgICJsaXZlX3BlcmZvcm1hbmNlX2RhdGVzIjogWyIyMDIyLTAxLTE0IDExOjM2OjUxLjc4OTI1MyIsICIyMDIyLTAxLTE0IDExOjM3OjAzLjkyODk0NyJdLAogICAgImNhc3QiOiBbIjYxZTA2OTc0N2M4ZjExOTg2ZjgwZmVhMSJdLAogICAgImF1ZGl0aW9ucyI6IFsiNjFlMDY5NzQ3YzhmMTE5ODZmODBmZWExIl0sCiAgICAidmVudWUiOiAiMTIzIE1pZG8gTm93aGVyZSBMYW5lIgp9",
    "isBase64Encoded": True
}

# Example performance before its Base64 encoded
{
    "title": "another performance",
    "director": "61e1be1a56377e88b5aac8a9",
    "casting_director": "61e1be1a56377e88b5aac8a9",
    "live_performance_dates": ["2022-01-14 11:36:51.789253", "2022-01-14 11:37:03.928947"],
    "cast": ["61e069747c8f11986f80fea1"],
    "auditions": ["61e069747c8f11986f80fea1"],
    "venue": "123 Mido Nowhere Lane"
}
# d = datetime.datetime.fromisoformat("2022-01-14 11:37:03.928947")

print(lambda_handler(data, None))
