from unittest.mock import MagicMock, patch

import boto3
from botocore.exceptions import ClientError
from moto import mock_dynamodb

from src.handlers.delete_todo import get_dynamodb_client, lambda_handler


class TestDeleteTodo:
    """delete_todo Lambda関数のテストクラス"""

    def test_lambda_handler_missing_todo_id(self):
        """todo_idが不足している場合のテスト"""
        # Given
        event = {"pathParameters": None}
        context = {}

        # When
        response = lambda_handler(event, context)

        # Then
        assert response["statusCode"] == 400
        assert "Todo ID is required" in response["body"]

    def test_lambda_handler_empty_todo_id(self):
        """todo_idが空の場合のテスト"""
        # Given
        event = {"pathParameters": {"id": ""}}
        context = {}

        # When
        response = lambda_handler(event, context)

        # Then
        assert response["statusCode"] == 400
        assert "Todo ID is required" in response["body"]

    def test_lambda_handler_todo_not_found(self):
        """Todoが見つからない場合のテスト"""
        # Given
        event = {
            "pathParameters": {"id": "nonexistent"},
            "queryStringParameters": {"user_id": "user123"},
        }
        context = {}

        # 存在しないTodoのレスポンスをモック
        mock_client = MagicMock()
        mock_client.get_item.return_value = {}  # 'Item'キーなし

        with patch(
            "src.handlers.delete_todo.get_dynamodb_client", return_value=mock_client
        ):
            # When
            response = lambda_handler(event, context)

        # Then
        assert response["statusCode"] == 404
        assert "Todo not found" in response["body"]

    @mock_dynamodb
    def test_lambda_handler_success_with_query_user_id(self):
        """正常動作 - クエリパラメータでuser_idを指定"""
        # Given
        # DynamoDBテーブルを作成
        dynamodb = boto3.client("dynamodb", region_name="us-east-1")
        dynamodb.create_table(
            TableName="todos",
            KeySchema=[
                {"AttributeName": "user_id", "KeyType": "HASH"},
                {"AttributeName": "todo_id", "KeyType": "RANGE"},
            ],
            AttributeDefinitions=[
                {"AttributeName": "user_id", "AttributeType": "S"},
                {"AttributeName": "todo_id", "AttributeType": "S"},
            ],
            BillingMode="PAY_PER_REQUEST",
        )

        # 既存のTodoを挿入
        dynamodb.put_item(
            TableName="todos",
            Item={
                "user_id": {"S": "user123"},
                "todo_id": {"S": "todo1"},
                "title": {"S": "Test Todo"},
                "description": {"S": "Test Description"},
                "completed": {"BOOL": False},
                "priority": {"S": "medium"},
                "created_at": {"S": "2025-01-01T00:00:00"},
                "updated_at": {"S": "2025-01-01T00:00:00"},
            },
        )

        event = {
            "pathParameters": {"id": "todo1"},
            "queryStringParameters": {"user_id": "user123"},
        }
        context = {}

        # DynamoDBクライアントをモック
        with patch(
            "src.handlers.delete_todo.get_dynamodb_client", return_value=dynamodb
        ):
            # When
            response = lambda_handler(event, context)

        # Then
        assert response["statusCode"] == 204
        assert response["body"] == ""

        # Todoが削除されているか確認
        result = dynamodb.get_item(
            TableName="todos",
            Key={"user_id": {"S": "user123"}, "todo_id": {"S": "todo1"}},
        )
        assert "Item" not in result

    @mock_dynamodb
    def test_lambda_handler_success_default_user_id(self):
        """正常動作 - デフォルトuser_idを使用"""
        # Given
        # DynamoDBテーブルを作成
        dynamodb = boto3.client("dynamodb", region_name="us-east-1")
        dynamodb.create_table(
            TableName="todos",
            KeySchema=[
                {"AttributeName": "user_id", "KeyType": "HASH"},
                {"AttributeName": "todo_id", "KeyType": "RANGE"},
            ],
            AttributeDefinitions=[
                {"AttributeName": "user_id", "AttributeType": "S"},
                {"AttributeName": "todo_id", "AttributeType": "S"},
            ],
            BillingMode="PAY_PER_REQUEST",
        )

        # 既存のTodoを挿入（デフォルトuser_id）
        dynamodb.put_item(
            TableName="todos",
            Item={
                "user_id": {"S": "user123"},
                "todo_id": {"S": "todo1"},
                "title": {"S": "Test Todo"},
                "description": {"S": "Test Description"},
                "completed": {"BOOL": False},
                "priority": {"S": "medium"},
                "created_at": {"S": "2025-01-01T00:00:00"},
                "updated_at": {"S": "2025-01-01T00:00:00"},
            },
        )

        event = {"pathParameters": {"id": "todo1"}}
        context = {}

        # DynamoDBクライアントをモック
        with patch(
            "src.handlers.delete_todo.get_dynamodb_client", return_value=dynamodb
        ):
            # When
            response = lambda_handler(event, context)

        # Then
        assert response["statusCode"] == 204
        assert response["body"] == ""

        # Todoが削除されているか確認
        result = dynamodb.get_item(
            TableName="todos",
            Key={"user_id": {"S": "user123"}, "todo_id": {"S": "todo1"}},
        )
        assert "Item" not in result

    def test_lambda_handler_dynamodb_get_error(self):
        """DynamoDB get_item エラーのテスト"""
        # Given
        event = {
            "pathParameters": {"id": "todo1"},
            "queryStringParameters": {"user_id": "user123"},
        }
        context = {}

        # DynamoDBクライアントがエラーを発生させる
        mock_client = MagicMock()
        mock_client.get_item.side_effect = ClientError(
            {
                "Error": {
                    "Code": "ResourceNotFoundException",
                    "Message": "Table not found",
                }
            },
            "GetItem",
        )

        with patch(
            "src.handlers.delete_todo.get_dynamodb_client", return_value=mock_client
        ):
            # When
            response = lambda_handler(event, context)

        # Then
        assert response["statusCode"] == 500
        assert "Failed to fetch todo" in response["body"]

    def test_lambda_handler_dynamodb_delete_error(self):
        """DynamoDB delete_item エラーのテスト"""
        # Given
        event = {
            "pathParameters": {"id": "todo1"},
            "queryStringParameters": {"user_id": "user123"},
        }
        context = {}

        # DynamoDBクライアントの設定
        mock_client = MagicMock()
        mock_client.get_item.return_value = {
            "Item": {
                "user_id": {"S": "user123"},
                "todo_id": {"S": "todo1"},
                "title": {"S": "Test Todo"},
            }
        }
        mock_client.delete_item.side_effect = ClientError(
            {
                "Error": {
                    "Code": "ResourceNotFoundException",
                    "Message": "Table not found",
                }
            },
            "DeleteItem",
        )

        with patch(
            "src.handlers.delete_todo.get_dynamodb_client", return_value=mock_client
        ):
            # When
            response = lambda_handler(event, context)

        # Then
        assert response["statusCode"] == 500
        assert "Failed to delete todo" in response["body"]

    def test_lambda_handler_unexpected_error(self):
        """予期しないエラーのテスト"""
        # Given
        event = {
            "pathParameters": {"id": "todo1"},
            "queryStringParameters": {"user_id": "user123"},
        }
        context = {}

        # DynamoDBクライアントが予期しないエラーを発生させる
        mock_client = MagicMock()
        mock_client.get_item.side_effect = Exception("Unexpected error")

        with patch(
            "src.handlers.delete_todo.get_dynamodb_client", return_value=mock_client
        ):
            # When
            response = lambda_handler(event, context)

        # Then
        assert response["statusCode"] == 500
        assert "Internal server error" in response["body"]

    def test_cors_headers(self):
        """CORSヘッダーのテスト"""
        # Given
        event = {
            "pathParameters": {"id": "todo1"},
            "queryStringParameters": {"user_id": "user123"},
        }
        context = {}

        mock_client = MagicMock()
        mock_client.get_item.return_value = {
            "Item": {
                "user_id": {"S": "user123"},
                "todo_id": {"S": "todo1"},
                "title": {"S": "Test Todo"},
            }
        }
        mock_client.delete_item.return_value = {}

        with patch(
            "src.handlers.delete_todo.get_dynamodb_client", return_value=mock_client
        ):
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
        assert hasattr(client, "get_item")
        assert hasattr(client, "delete_item")
        assert hasattr(client, "put_item")
        assert hasattr(client, "query")
