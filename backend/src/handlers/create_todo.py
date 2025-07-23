import json
import os
import uuid
from datetime import datetime

import boto3
from botocore.exceptions import ClientError

# LocalStack環境の設定
DYNAMODB_ENDPOINT = os.environ.get(
    "DYNAMODB_ENDPOINT", "http://host.docker.internal:4566"
)
TABLE_NAME = os.environ.get("TABLE_NAME", "todos")


def get_dynamodb_client():
    """DynamoDB クライアントを取得"""
    return boto3.client(
        "dynamodb",
        endpoint_url=DYNAMODB_ENDPOINT,
        aws_access_key_id="test",
        aws_secret_access_key="test",
        region_name="us-east-1",
    )


def lambda_handler(event, context):
    """Create a new todo - minimal implementation"""

    try:
        # Parse request body
        body = json.loads(event.get("body", "{}"))

        # Basic validation
        if not body.get("title"):
            return {
                "statusCode": 400,
                "headers": {
                    "Content-Type": "application/json",
                    "Access-Control-Allow-Origin": "*",
                },
                "body": json.dumps(
                    {"error": "Title is required", "code": "VALIDATION_ERROR"}
                ),
            }

        # Create new todo
        user_id = body.get("user_id", "user123")
        todo_id = str(uuid.uuid4())
        now = datetime.now().isoformat()

        new_todo = {
            "user_id": user_id,
            "todo_id": todo_id,
            "title": body.get("title"),
            "description": body.get("description", ""),
            "completed": False,
            "priority": body.get("priority", "medium"),
            "created_at": now,
            "updated_at": now,
        }

        # DynamoDB クライアントを取得
        dynamodb = get_dynamodb_client()

        # DynamoDB にデータを保存
        dynamodb.put_item(
            TableName=TABLE_NAME,
            Item={
                "user_id": {"S": user_id},
                "todo_id": {"S": todo_id},
                "title": {"S": new_todo["title"]},
                "description": {"S": new_todo["description"]},
                "completed": {"BOOL": new_todo["completed"]},
                "priority": {"S": new_todo["priority"]},
                "created_at": {"S": new_todo["created_at"]},
                "updated_at": {"S": new_todo["updated_at"]},
            },
        )

        return {
            "statusCode": 201,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE",
                "Access-Control-Allow-Headers": "Content-Type",
            },
            "body": json.dumps(new_todo),
        }

    except ClientError as e:
        print(f"DynamoDB error: {e}")
        return {
            "statusCode": 500,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
            },
            "body": json.dumps(
                {"error": "Failed to create todo", "code": "INTERNAL_ERROR"}
            ),
        }
    except json.JSONDecodeError:
        return {
            "statusCode": 400,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
            },
            "body": json.dumps(
                {"error": "Invalid JSON in request body", "code": "BAD_REQUEST"}
            ),
        }
    except Exception as e:
        print(f"Unexpected error: {e}")
        return {
            "statusCode": 500,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
            },
            "body": json.dumps(
                {"error": "Internal server error", "code": "INTERNAL_ERROR"}
            ),
        }
