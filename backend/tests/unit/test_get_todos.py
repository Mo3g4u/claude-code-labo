import json
import pytest
from unittest.mock import patch, MagicMock
from moto import mock_dynamodb
import boto3
from botocore.exceptions import ClientError

from src.handlers.get_todos import lambda_handler, get_dynamodb_client


class TestGetTodos:
    """get_todos Lambda関数のテストクラス"""
    
    def test_lambda_handler_missing_user_id(self):
        """user_idが不足している場合のテスト"""
        # Given
        event = {
            "queryStringParameters": None
        }
        context = {}
        
        # When
        response = lambda_handler(event, context)
        
        # Then
        assert response["statusCode"] == 400
        assert "user_id is required" in response["body"]
    
    def test_lambda_handler_empty_user_id(self):
        """user_idが空の場合のテスト"""
        # Given
        event = {
            "queryStringParameters": {"user_id": ""}
        }
        context = {}
        
        # When
        response = lambda_handler(event, context)
        
        # Then
        assert response["statusCode"] == 400
        assert "user_id is required" in response["body"]
    
    @mock_dynamodb
    def test_lambda_handler_success_empty_result(self):
        """正常動作 - 空の結果のテスト"""
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
            "queryStringParameters": {"user_id": "user123"}
        }
        context = {}
        
        # DynamoDBクライアントをモック
        with patch('src.handlers.get_todos.get_dynamodb_client', return_value=dynamodb):
            # When
            response = lambda_handler(event, context)
        
        # Then
        assert response["statusCode"] == 200
        body = json.loads(response["body"])
        assert body["todos"] == []
        assert body["count"] == 0
    
    @mock_dynamodb
    def test_lambda_handler_success_with_data(self):
        """正常動作 - データありのテスト"""
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
        
        # テストデータを挿入
        dynamodb.put_item(
            TableName='todos',
            Item={
                'user_id': {'S': 'user123'},
                'todo_id': {'S': 'todo1'},
                'title': {'S': 'Test Todo'},
                'description': {'S': 'Test Description'},
                'completed': {'BOOL': False},
                'priority': {'S': 'high'},
                'created_at': {'S': '2025-01-01T00:00:00'},
                'updated_at': {'S': '2025-01-01T00:00:00'}
            }
        )
        
        event = {
            "queryStringParameters": {"user_id": "user123"}
        }
        context = {}
        
        # DynamoDBクライアントをモック
        with patch('src.handlers.get_todos.get_dynamodb_client', return_value=dynamodb):
            # When
            response = lambda_handler(event, context)
        
        # Then
        assert response["statusCode"] == 200
        body = json.loads(response["body"])
        assert len(body["todos"]) == 1
        assert body["count"] == 1
        assert body["todos"][0]["user_id"] == "user123"
        assert body["todos"][0]["todo_id"] == "todo1"
        assert body["todos"][0]["title"] == "Test Todo"
        assert body["todos"][0]["completed"] is False
    
    def test_lambda_handler_dynamodb_error(self):
        """DynamoDBエラーのテスト"""
        # Given
        event = {
            "queryStringParameters": {"user_id": "user123"}
        }
        context = {}
        
        # DynamoDBクライアントがエラーを発生させる
        mock_client = MagicMock()
        mock_client.query.side_effect = ClientError(
            {'Error': {'Code': 'ResourceNotFoundException', 'Message': 'Table not found'}},
            'Query'
        )
        
        with patch('src.handlers.get_todos.get_dynamodb_client', return_value=mock_client):
            # When
            response = lambda_handler(event, context)
        
        # Then
        assert response["statusCode"] == 500
        assert "Failed to fetch todos" in response["body"]
    
    def test_lambda_handler_unexpected_error(self):
        """予期しないエラーのテスト"""
        # Given
        event = {
            "queryStringParameters": {"user_id": "user123"}
        }
        context = {}
        
        # DynamoDBクライアントが予期しないエラーを発生させる
        mock_client = MagicMock()
        mock_client.query.side_effect = Exception("Unexpected error")
        
        with patch('src.handlers.get_todos.get_dynamodb_client', return_value=mock_client):
            # When
            response = lambda_handler(event, context)
        
        # Then
        assert response["statusCode"] == 500
        assert "Internal server error" in response["body"]
    
    def test_cors_headers(self):
        """CORSヘッダーのテスト"""
        # Given
        event = {
            "queryStringParameters": {"user_id": "user123"}
        }
        context = {}
        
        mock_client = MagicMock()
        mock_client.query.return_value = {"Items": []}
        
        with patch('src.handlers.get_todos.get_dynamodb_client', return_value=mock_client):
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
        assert hasattr(client, 'query')
        assert hasattr(client, 'put_item')
        assert hasattr(client, 'get_item')
        assert hasattr(client, 'delete_item')