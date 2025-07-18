import json
import uuid
from datetime import datetime

def lambda_handler(event, context):
    """Get a specific todo - minimal implementation"""
    
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
    
    # Mock data for testing
    mock_todo = {
        "user_id": "user123",
        "todo_id": todo_id,
        "title": "Sample Todo",
        "description": "This is a sample todo",
        "completed": False,
        "priority": "medium",
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    }
    
    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE",
            "Access-Control-Allow-Headers": "Content-Type"
        },
        "body": json.dumps(mock_todo)
    }