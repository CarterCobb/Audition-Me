import os
import boto3
from base64 import b64decode
from json import loads

SENDER = "Audition Me API <carter.cobb72@gmail.com>"
AWS_REGION = "us-west-1"
CHARSET = "UTF-8"
ses = boto3.client("ses")


def lambda_handler(event, context):
    """
    All `to` emails must be verifyed in SES to work. Otherwise you will get an error when sending an email to an unverified email.
    """
    try:
        req_body = event["body"]
        if ("isBase64Encoded" in event and event["isBase64Encoded"]):
            req_body = loads(b64decode(req_body))
        if "to" in req_body and 'message' in req_body and "subject" in req_body:
            ses.send_email(
                Destination={
                    "ToAddresses": [req_body["to"]]
                },
                Message={
                    "Body": {
                        "Text": {
                            "Charset": CHARSET,
                            "Data": req_body["message"]
                        }
                    },
                    "Subject": {
                        "Charset": CHARSET,
                        "Data": req_body["subject"]
                    }
                },
                Source=SENDER
            )
            return {"statusCode": 204}
        else:
            return {
                "statusCode": 400,
                "error": "MISSING_BODY_VALUES",
                "message": "missing `subject`, `to` or `message` properties in the request body"
            }
    except Exception as e:
        return {
            "statusCode": 500,
            "error": "SERVER_ERROR",
            "message": str(e)
        }


# TESTING

# data = {
#     "body": "ewogICAgInRvIjogInRlc3RAdGVzdC5jb20iLAogICAgInN1YmplY3QiOiAidGVzdCIsCiAgICAibWVzc2FnZSI6ICJ0ZXN0IG1lc3NhZ2UgOikiCn0=",
#     "isBase64Encoded": True
# }

# {
    # "to": "test@test.com",
    # "subject": "test",
    # "message": "test message :)"
# }

# print(lambda_handler(data, None))
