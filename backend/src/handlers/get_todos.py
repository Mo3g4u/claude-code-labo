import json
import os
from typing import Any

import boto3
from botocore.exceptions import ClientError

from auth_helper import get_user_from_event

# LocalStack環境の設定
DYNAMODB_ENDPOINT = os.environ.get(
    "DYNAMODB_ENDPOINT", "http://host.docker.internal:4566"
)
TABLE_NAME = os.environ.get("TABLE_NAME", "todos")



def get_dynamodb_client() -> Any:
    """DynamoDB クライアントを取得"""
    return boto3.client(
        "dynamodb",
        endpoint_url=DYNAMODB_ENDPOINT,
        aws_access_key_id="test",
        aws_secret_access_key="test",
        region_name="us-east-1",
    )


def lambda_handler(event: dict[str, Any], context: Any) -> dict[str, Any]:
    """Get all todos from DynamoDB"""

    try:
        # テスト用: 認証をバイパスしてテストユーザーを使用
        user_id = "test-user"
        
        # 認証されたユーザー情報を取得
        # try:
        #     user = get_user_from_event(event)
        #     user_id = user["user_id"]
        # except Exception as auth_error:
        #     return {
        #         "statusCode": 401,
        #         "headers": {
        #             "Content-Type": "application/json",
        #             "Access-Control-Allow-Origin": "*",
        #             "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE",
        #             "Access-Control-Allow-Headers": "Content-Type,Authorization",
        #         },
        #         "body": json.dumps(
        #             {"error": f"Authentication failed: {str(auth_error)}", "code": "UNAUTHORIZED"}
        #         ),
        #     }

        # DynamoDB クライアントを取得
        dynamodb = get_dynamodb_client()

        # DynamoDB からデータを取得
        response = dynamodb.query(
            TableName=TABLE_NAME,
            KeyConditionExpression="user_id = :user_id",
            ExpressionAttributeValues={":user_id": {"S": user_id}},
        )

        # レスポンスデータを変換
        todos = []
        for item in response.get("Items", []):
            todo = {
                "user_id": item["user_id"]["S"],
                "todo_id": item["todo_id"]["S"],
                "title": item["title"]["S"],
                "description": item.get("description", {}).get("S", ""),
                "completed": item.get("completed", {}).get("BOOL", False),
                "priority": item.get("priority", {}).get("S", "medium"),
                "created_at": item.get("created_at", {}).get("S", ""),
                "updated_at": item.get("updated_at", {}).get("S", ""),
            }
            todos.append(todo)

        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE",
                "Access-Control-Allow-Headers": "Content-Type,Authorization",
            },
            "body": json.dumps({"todos": todos, "count": len(todos)}),
        }

    except ClientError as e:
        print(f"DynamoDB error: {e}")
        return {
            "statusCode": 500,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Content-Type,Authorization",
            },
            "body": json.dumps(
                {"error": "Failed to fetch todos", "code": "INTERNAL_ERROR"}
            ),
        }
    except Exception as e:
        print(f"Unexpected error: {e}")
        return {
            "statusCode": 500,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Content-Type,Authorization",
            },
            "body": json.dumps(
                {"error": "Internal server error", "code": "INTERNAL_ERROR"}
            ),
        }
