import json
import uuid
import boto3
import os
from datetime import datetime
from botocore.exceptions import ClientError

# LocalStack環境の設定
DYNAMODB_ENDPOINT = os.environ.get('DYNAMODB_ENDPOINT', 'http://host.docker.internal:4566')
TABLE_NAME = os.environ.get('TABLE_NAME', 'todos')

def get_dynamodb_client():
    """DynamoDB クライアントを取得"""
    return boto3.client(
        'dynamodb',
        endpoint_url=DYNAMODB_ENDPOINT,
        aws_access_key_id='test',
        aws_secret_access_key='test',
        region_name='us-east-1'
    )

def lambda_handler(event, context):
    """Update a todo - minimal implementation"""
    
    try:
        # Extract todo_id from path parameters
        todo_id = event.get('pathParameters', {}).get('id')
        
        if not todo_id:
            return {
                "statusCode": 400,
                "headers": {
                    "Content-Type": "application/json",
                    "Access-Control-Allow-Origin": "*"
                },
                "body": json.dumps({
                    "error": "Todo ID is required",
                    "code": "BAD_REQUEST"
                })
            }
        
        # Parse request body
        body = json.loads(event.get('body', '{}'))
        user_id = body.get('user_id', 'user123')
        
        # DynamoDB クライアントを取得
        dynamodb = get_dynamodb_client()
        
        # 現在のデータを取得
        try:
            response = dynamodb.get_item(
                TableName=TABLE_NAME,
                Key={
                    'user_id': {'S': user_id},
                    'todo_id': {'S': todo_id}
                }
            )
        except ClientError as e:
            print(f"DynamoDB get_item error: {e}")
            return {
                "statusCode": 500,
                "headers": {
                    "Content-Type": "application/json",
                    "Access-Control-Allow-Origin": "*"
                },
                "body": json.dumps({
                    "error": "Failed to fetch todo",
                    "code": "INTERNAL_ERROR"
                })
            }
        
        if 'Item' not in response:
            return {
                "statusCode": 404,
                "headers": {
                    "Content-Type": "application/json",
                    "Access-Control-Allow-Origin": "*"
                },
                "body": json.dumps({
                    "error": "Todo not found",
                    "code": "NOT_FOUND"
                })
            }
        
        # 現在のデータを取得
        current_todo = response['Item']
        
        # 更新するフィールドを決定
        updated_todo = {
            "user_id": user_id,
            "todo_id": todo_id,
            "title": body.get('title', current_todo.get('title', {}).get('S', '')),
            "description": body.get('description', current_todo.get('description', {}).get('S', '')),
            "completed": body.get('completed', current_todo.get('completed', {}).get('BOOL', False)),
            "priority": body.get('priority', current_todo.get('priority', {}).get('S', 'medium')),
            "created_at": current_todo.get('created_at', {}).get('S', ''),
            "updated_at": datetime.now().isoformat()
        }
        
        # DynamoDB にデータを更新
        dynamodb.put_item(
            TableName=TABLE_NAME,
            Item={
                'user_id': {'S': updated_todo['user_id']},
                'todo_id': {'S': updated_todo['todo_id']},
                'title': {'S': updated_todo['title']},
                'description': {'S': updated_todo['description']},
                'completed': {'BOOL': updated_todo['completed']},
                'priority': {'S': updated_todo['priority']},
                'created_at': {'S': updated_todo['created_at']},
                'updated_at': {'S': updated_todo['updated_at']}
            }
        )
        
        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE",
                "Access-Control-Allow-Headers": "Content-Type"
            },
            "body": json.dumps(updated_todo)
        }
        
    except ClientError as e:
        print(f"DynamoDB error: {e}")
        return {
            "statusCode": 500,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*"
            },
            "body": json.dumps({
                "error": "Failed to update todo",
                "code": "INTERNAL_ERROR"
            })
        }
    except json.JSONDecodeError:
        return {
            "statusCode": 400,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*"
            },
            "body": json.dumps({
                "error": "Invalid JSON in request body",
                "code": "BAD_REQUEST"
            })
        }
    except Exception as e:
        print(f"Unexpected error: {e}")
        return {
            "statusCode": 500,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*"
            },
            "body": json.dumps({
                "error": "Internal server error",
                "code": "INTERNAL_ERROR"
            })
        }