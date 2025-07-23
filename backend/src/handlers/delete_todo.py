import json
import os

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
    """Delete a todo from DynamoDB"""

    try:
        # Extract todo_id from path parameters
        path_params = event.get("pathParameters") or {}
        todo_id = path_params.get("id")

        if not todo_id:
            return {
                "statusCode": 400,
                "headers": {
                    "Content-Type": "application/json",
                    "Access-Control-Allow-Origin": "*",
                },
                "body": json.dumps(
                    {"error": "Todo ID is required", "code": "BAD_REQUEST"}
                ),
            }

        # user_idを取得（クエリパラメータから、またはデフォルト値を使用）
        query_params = event.get("queryStringParameters") or {}
        user_id = query_params.get("user_id", "user123")

        # DynamoDB クライアントを取得
        dynamodb = get_dynamodb_client()

        # 削除する前にアイテムが存在するか確認
        try:
            response = dynamodb.get_item(
                TableName=TABLE_NAME,
                Key={"user_id": {"S": user_id}, "todo_id": {"S": todo_id}},
            )
        except ClientError as e:
            print(f"DynamoDB get_item error: {e}")
            return {
                "statusCode": 500,
                "headers": {
                    "Content-Type": "application/json",
                    "Access-Control-Allow-Origin": "*",
                },
                "body": json.dumps(
                    {"error": "Failed to fetch todo", "code": "INTERNAL_ERROR"}
                ),
            }

        if "Item" not in response:
            return {
                "statusCode": 404,
                "headers": {
                    "Content-Type": "application/json",
                    "Access-Control-Allow-Origin": "*",
                },
                "body": json.dumps({"error": "Todo not found", "code": "NOT_FOUND"}),
            }

        # DynamoDB からアイテムを削除
        dynamodb.delete_item(
            TableName=TABLE_NAME,
            Key={"user_id": {"S": user_id}, "todo_id": {"S": todo_id}},
        )

        return {
            "statusCode": 204,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE",
                "Access-Control-Allow-Headers": "Content-Type",
            },
            "body": "",
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
                {"error": "Failed to delete todo", "code": "INTERNAL_ERROR"}
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
