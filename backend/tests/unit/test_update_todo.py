import json
from unittest.mock import MagicMock, patch

import boto3
from botocore.exceptions import ClientError
from moto import mock_dynamodb

from src.handlers.update_todo import lambda_handler


class TestUpdateTodo:
    """update_todo Lambda関数のテストクラス"""

    def test_lambda_handler_missing_todo_id(self):
        """todo_idが不足している場合のテスト"""
        # Given
        event = {"pathParameters": None, "body": json.dumps({"title": "Updated Todo"})}
        context = {}

        # When
        response = lambda_handler(event, context)

        # Then
        assert response["statusCode"] == 400
        assert "Todo ID is required" in response["body"]

    def test_lambda_handler_empty_todo_id(self):
        """todo_idが空の場合のテスト"""
        # Given
        event = {
            "pathParameters": {"id": ""},
            "body": json.dumps({"title": "Updated Todo"}),
        }
        context = {}

        # When
        response = lambda_handler(event, context)

        # Then
        assert response["statusCode"] == 400
        assert "Todo ID is required" in response["body"]

    def test_lambda_handler_invalid_json(self):
        """不正なJSONの場合のテスト"""
        # Given
        event = {"pathParameters": {"id": "todo1"}, "body": "invalid json"}
        context = {}

        # When
        response = lambda_handler(event, context)

        # Then
        assert response["statusCode"] == 400
        assert "Invalid JSON in request body" in response["body"]

    def test_lambda_handler_todo_not_found(self):
        """Todoが見つからない場合のテスト"""
        # Given
        event = {
            "pathParameters": {"id": "nonexistent"},
            "body": json.dumps({"title": "Updated Todo"}),
        }
        context = {}

        # 存在しないTodoのレスポンスをモック
        mock_client = MagicMock()
        mock_client.get_item.return_value = {}  # 'Item'キーなし

        with patch(
            "src.handlers.update_todo.get_dynamodb_client", return_value=mock_client
        ):
            # When
            response = lambda_handler(event, context)

        # Then
        assert response["statusCode"] == 404
        assert "Todo not found" in response["body"]

    @mock_dynamodb
    def test_lambda_handler_success_partial_update(self):
        """正常動作 - 部分更新のテスト"""
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
                "title": {"S": "Original Title"},
                "description": {"S": "Original Description"},
                "completed": {"BOOL": False},
                "priority": {"S": "low"},
                "created_at": {"S": "2025-01-01T00:00:00"},
                "updated_at": {"S": "2025-01-01T00:00:00"},
            },
        )

        event = {
            "pathParameters": {"id": "todo1"},
            "body": json.dumps({"title": "Updated Title"}),
        }
        context = {}

        # DynamoDBクライアントをモック
        with patch(
            "src.handlers.update_todo.get_dynamodb_client", return_value=dynamodb
        ):
            # When
            response = lambda_handler(event, context)

        # Then
        assert response["statusCode"] == 200
        body = json.loads(response["body"])
        assert body["title"] == "Updated Title"
        assert body["description"] == "Original Description"  # 変更されていない
        assert body["completed"] is False
        assert body["priority"] == "low"
        assert body["user_id"] == "user123"
        assert body["todo_id"] == "todo1"
        assert body["created_at"] == "2025-01-01T00:00:00"
        assert body["updated_at"] != "2025-01-01T00:00:00"  # 更新されている

    @mock_dynamodb
    def test_lambda_handler_success_full_update(self):
        """正常動作 - 全項目更新のテスト"""
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
                "title": {"S": "Original Title"},
                "description": {"S": "Original Description"},
                "completed": {"BOOL": False},
                "priority": {"S": "low"},
                "created_at": {"S": "2025-01-01T00:00:00"},
                "updated_at": {"S": "2025-01-01T00:00:00"},
            },
        )

        event = {
            "pathParameters": {"id": "todo1"},
            "body": json.dumps(
                {
                    "title": "Updated Title",
                    "description": "Updated Description",
                    "completed": True,
                    "priority": "high",
                }
            ),
        }
        context = {}

        # DynamoDBクライアントをモック
        with patch(
            "src.handlers.update_todo.get_dynamodb_client", return_value=dynamodb
        ):
            # When
            response = lambda_handler(event, context)

        # Then
        assert response["statusCode"] == 200
        body = json.loads(response["body"])
        assert body["title"] == "Updated Title"
        assert body["description"] == "Updated Description"
        assert body["completed"] is True
        assert body["priority"] == "high"
        assert body["user_id"] == "user123"
        assert body["todo_id"] == "todo1"
        assert body["created_at"] == "2025-01-01T00:00:00"
        assert body["updated_at"] != "2025-01-01T00:00:00"

    def test_lambda_handler_dynamodb_get_error(self):
        """DynamoDB get_item エラーのテスト"""
        # Given
        event = {
            "pathParameters": {"id": "todo1"},
            "body": json.dumps({"title": "Updated Todo"}),
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
            "src.handlers.update_todo.get_dynamodb_client", return_value=mock_client
        ):
            # When
            response = lambda_handler(event, context)

        # Then
        assert response["statusCode"] == 500
        assert "Failed to fetch todo" in response["body"]

    def test_lambda_handler_dynamodb_put_error(self):
        """DynamoDB put_item エラーのテスト"""
        # Given
        event = {
            "pathParameters": {"id": "todo1"},
            "body": json.dumps({"title": "Updated Todo"}),
        }
        context = {}

        # DynamoDBクライアントの設定
        mock_client = MagicMock()
        mock_client.get_item.return_value = {
            "Item": {
                "user_id": {"S": "user123"},
                "todo_id": {"S": "todo1"},
                "title": {"S": "Original Title"},
                "description": {"S": "Original Description"},
                "completed": {"BOOL": False},
                "priority": {"S": "low"},
                "created_at": {"S": "2025-01-01T00:00:00"},
                "updated_at": {"S": "2025-01-01T00:00:00"},
            }
        }
        mock_client.put_item.side_effect = ClientError(
            {
                "Error": {
                    "Code": "ResourceNotFoundException",
                    "Message": "Table not found",
                }
            },
            "PutItem",
        )

        with patch(
            "src.handlers.update_todo.get_dynamodb_client", return_value=mock_client
        ):
            # When
            response = lambda_handler(event, context)

        # Then
        assert response["statusCode"] == 500
        assert "Failed to update todo" in response["body"]

    def test_lambda_handler_unexpected_error(self):
        """予期しないエラーのテスト"""
        # Given
        event = {
            "pathParameters": {"id": "todo1"},
            "body": json.dumps({"title": "Updated Todo"}),
        }
        context = {}

        # DynamoDBクライアントが予期しないエラーを発生させる
        mock_client = MagicMock()
        mock_client.get_item.side_effect = Exception("Unexpected error")

        with patch(
            "src.handlers.update_todo.get_dynamodb_client", return_value=mock_client
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
            "body": json.dumps({"title": "Updated Todo"}),
        }
        context = {}

        mock_client = MagicMock()
        mock_client.get_item.return_value = {
            "Item": {
                "user_id": {"S": "user123"},
                "todo_id": {"S": "todo1"},
                "title": {"S": "Original Title"},
                "description": {"S": "Original Description"},
                "completed": {"BOOL": False},
                "priority": {"S": "low"},
                "created_at": {"S": "2025-01-01T00:00:00"},
                "updated_at": {"S": "2025-01-01T00:00:00"},
            }
        }
        mock_client.put_item.return_value = {}

        with patch(
            "src.handlers.update_todo.get_dynamodb_client", return_value=mock_client
        ):
            # When
            response = lambda_handler(event, context)

        # Then
        headers = response["headers"]
        assert headers["Access-Control-Allow-Origin"] == "*"
        assert "GET, POST, PUT, DELETE" in headers["Access-Control-Allow-Methods"]
        assert "Content-Type" in headers["Access-Control-Allow-Headers"]
