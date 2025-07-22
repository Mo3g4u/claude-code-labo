import json
import pytest
from unittest.mock import patch, MagicMock
from moto import mock_dynamodb
import boto3
from botocore.exceptions import ClientError

from src.handlers.create_todo import lambda_handler, get_dynamodb_client


class TestCreateTodo:
    """create_todo Lambda関数のテストクラス"""
    
    def test_lambda_handler_missing_title(self):
        """titleが不足している場合のテスト"""
        # Given
        event = {
            "body": json.dumps({"user_id": "user123"})
        }
        context = {}
        
        # When
        response = lambda_handler(event, context)
        
        # Then
        assert response["statusCode"] == 400
        assert "Title is required" in response["body"]
    
    def test_lambda_handler_empty_title(self):
        """titleが空の場合のテスト"""
        # Given
        event = {
            "body": json.dumps({"title": "", "user_id": "user123"})
        }
        context = {}
        
        # When
        response = lambda_handler(event, context)
        
        # Then
        assert response["statusCode"] == 400
        assert "Title is required" in response["body"]
    
    def test_lambda_handler_invalid_json(self):
        """不正なJSONの場合のテスト"""
        # Given
        event = {
            "body": "invalid json"
        }
        context = {}
        
        # When
        response = lambda_handler(event, context)
        
        # Then
        assert response["statusCode"] == 400
        assert "Invalid JSON in request body" in response["body"]
    
    def test_lambda_handler_missing_body(self):
        """bodyが不足している場合のテスト"""
        # Given
        event = {}
        context = {}
        
        # When
        response = lambda_handler(event, context)
        
        # Then
        assert response["statusCode"] == 400
        assert "Title is required" in response["body"]
    
    @mock_dynamodb
    def test_lambda_handler_success_minimal(self):
        """正常動作 - 最小限のデータのテスト"""
        # Given
        # DynamoDBテーブルを作成
        dynamodb = boto3.client('dynamodb', region_name='us-east-1')
        dynamodb.create_table(
            TableName='todos',
            KeySchema=[
                {'AttributeName': 'user_id', 'KeyType': 'HASH'},
                {'AttributeName': 'todo_id', 'KeyType': 'RANGE'}
            ],
            AttributeDefinitions=[
                {'AttributeName': 'user_id', 'AttributeType': 'S'},
                {'AttributeName': 'todo_id', 'AttributeType': 'S'}
            ],
            BillingMode='PAY_PER_REQUEST'
        )
        
        event = {
            "body": json.dumps({"title": "Test Todo"})
        }
        context = {}
        
        # DynamoDBクライアントをモック
        with patch('src.handlers.create_todo.get_dynamodb_client', return_value=dynamodb):
            # When
            response = lambda_handler(event, context)
        
        # Then
        assert response["statusCode"] == 201
        body = json.loads(response["body"])
        assert body["title"] == "Test Todo"
        assert body["user_id"] == "user123"  # デフォルト値
        assert body["description"] == ""
        assert body["completed"] is False
        assert body["priority"] == "medium"
        assert "todo_id" in body
        assert "created_at" in body
        assert "updated_at" in body
    
    @mock_dynamodb
    def test_lambda_handler_success_full_data(self):
        """正常動作 - 全データのテスト"""
        # Given
        # DynamoDBテーブルを作成
        dynamodb = boto3.client('dynamodb', region_name='us-east-1')
        dynamodb.create_table(
            TableName='todos',
            KeySchema=[
                {'AttributeName': 'user_id', 'KeyType': 'HASH'},
                {'AttributeName': 'todo_id', 'KeyType': 'RANGE'}
            ],
            AttributeDefinitions=[
                {'AttributeName': 'user_id', 'AttributeType': 'S'},
                {'AttributeName': 'todo_id', 'AttributeType': 'S'}
            ],
            BillingMode='PAY_PER_REQUEST'
        )
        
        event = {
            "body": json.dumps({
                "title": "Test Todo",
                "description": "Test Description",
                "user_id": "custom_user",
                "priority": "high"
            })
        }
        context = {}
        
        # DynamoDBクライアントをモック
        with patch('src.handlers.create_todo.get_dynamodb_client', return_value=dynamodb):
            # When
            response = lambda_handler(event, context)
        
        # Then
        assert response["statusCode"] == 201
        body = json.loads(response["body"])
        assert body["title"] == "Test Todo"
        assert body["description"] == "Test Description"
        assert body["user_id"] == "custom_user"
        assert body["priority"] == "high"
        assert body["completed"] is False
        assert "todo_id" in body
        assert "created_at" in body
        assert "updated_at" in body
    
    def test_lambda_handler_dynamodb_error(self):
        """DynamoDBエラーのテスト"""
        # Given
        event = {
            "body": json.dumps({"title": "Test Todo"})
        }
        context = {}
        
        # DynamoDBクライアントがエラーを発生させる
        mock_client = MagicMock()
        mock_client.put_item.side_effect = ClientError(
            {'Error': {'Code': 'ResourceNotFoundException', 'Message': 'Table not found'}},
            'PutItem'
        )
        
        with patch('src.handlers.create_todo.get_dynamodb_client', return_value=mock_client):
            # When
            response = lambda_handler(event, context)
        
        # Then
        assert response["statusCode"] == 500
        assert "Failed to create todo" in response["body"]
    
    def test_lambda_handler_unexpected_error(self):
        """予期しないエラーのテスト"""
        # Given
        event = {
            "body": json.dumps({"title": "Test Todo"})
        }
        context = {}
        
        # DynamoDBクライアントが予期しないエラーを発生させる
        mock_client = MagicMock()
        mock_client.put_item.side_effect = Exception("Unexpected error")
        
        with patch('src.handlers.create_todo.get_dynamodb_client', return_value=mock_client):
            # When
            response = lambda_handler(event, context)
        
        # Then
        assert response["statusCode"] == 500
        assert "Internal server error" in response["body"]
    
    def test_cors_headers(self):
        """CORSヘッダーのテスト"""
        # Given
        event = {
            "body": json.dumps({"title": "Test Todo"})
        }
        context = {}
        
        mock_client = MagicMock()
        mock_client.put_item.return_value = {}
        
        with patch('src.handlers.create_todo.get_dynamodb_client', return_value=mock_client):
            # When
            response = lambda_handler(event, context)
        
        # Then
        headers = response["headers"]
        assert headers["Access-Control-Allow-Origin"] == "*"
        assert "GET, POST, PUT, DELETE" in headers["Access-Control-Allow-Methods"]
        assert "Content-Type" in headers["Access-Control-Allow-Headers"]
    
    def test_get_dynamodb_client(self):
        """DynamoDBクライアント取得のテスト"""
        # Given & When
        client = get_dynamodb_client()
        
        # Then
        assert client is not None
        assert hasattr(client, 'put_item')
        assert hasattr(client, 'get_item')
        assert hasattr(client, 'query')
        assert hasattr(client, 'delete_item')