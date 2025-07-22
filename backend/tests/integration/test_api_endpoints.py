import json
import pytest
import requests
import time
import subprocess
import os
import signal
from concurrent.futures import ThreadPoolExecutor
from unittest.mock import patch


class TestAPIEndpoints:
    """API エンドポイントの統合テスト"""
    
    @classmethod
    def setup_class(cls):
        """テストクラスの初期化"""
        cls.base_url = "http://127.0.0.1:3001"
        cls.user_id = "test_user"
        cls.created_todos = []
        
    def test_health_check(self):
        """APIサーバーの生存確認"""
        try:
            response = requests.get(f"{self.base_url}/todos", params={"user_id": self.user_id})
            assert response.status_code in [200, 500]  # サーバーが起動していることを確認
        except requests.exceptions.ConnectionError:
            pytest.skip("SAM local server is not running")
    
    def test_create_todo_success(self):
        """Todo作成の成功テスト"""
        # Given
        todo_data = {
            "user_id": self.user_id,
            "title": "Integration Test Todo",
            "description": "This is a test todo for integration testing",
            "priority": "high"
        }
        
        try:
            # When
            response = requests.post(
                f"{self.base_url}/todos",
                json=todo_data,
                headers={"Content-Type": "application/json"}
            )
            
            # Then
            assert response.status_code == 201
            data = response.json()
            assert data["title"] == todo_data["title"]
            assert data["description"] == todo_data["description"]
            assert data["user_id"] == self.user_id
            assert data["priority"] == "high"
            assert data["completed"] is False
            assert "todo_id" in data
            assert "created_at" in data
            assert "updated_at" in data
            
            # 作成されたTodoのIDを保存（後のテストで使用）
            self.created_todos.append(data["todo_id"])
            
        except requests.exceptions.ConnectionError:
            pytest.skip("SAM local server is not running")
    
    def test_create_todo_validation_error(self):
        """Todo作成のバリデーションエラーテスト"""
        # Given
        invalid_todo_data = {
            "user_id": self.user_id,
            "description": "Todo without title"
        }
        
        try:
            # When
            response = requests.post(
                f"{self.base_url}/todos",
                json=invalid_todo_data,
                headers={"Content-Type": "application/json"}
            )
            
            # Then
            assert response.status_code == 400
            data = response.json()
            assert "Title is required" in data["error"]
            
        except requests.exceptions.ConnectionError:
            pytest.skip("SAM local server is not running")
    
    def test_get_todos_success(self):
        """Todo一覧取得の成功テスト"""
        try:
            # When
            response = requests.get(f"{self.base_url}/todos", params={"user_id": self.user_id})
            
            # Then
            assert response.status_code == 200
            data = response.json()
            assert "todos" in data
            assert "count" in data
            assert isinstance(data["todos"], list)
            assert isinstance(data["count"], int)
            
            # 前のテストで作成したTodoが含まれているか確認
            if self.created_todos:
                todo_ids = [todo["todo_id"] for todo in data["todos"]]
                assert any(todo_id in todo_ids for todo_id in self.created_todos)
                
        except requests.exceptions.ConnectionError:
            pytest.skip("SAM local server is not running")
    
    def test_get_todos_missing_user_id(self):
        """Todo一覧取得でuser_id不足のテスト"""
        try:
            # When
            response = requests.get(f"{self.base_url}/todos")
            
            # Then
            assert response.status_code == 400
            data = response.json()
            assert "user_id is required" in data["error"]
            
        except requests.exceptions.ConnectionError:
            pytest.skip("SAM local server is not running")
    
    def test_update_todo_success(self):
        """Todo更新の成功テスト"""
        # 前提条件: Todoが作成されている
        if not self.created_todos:
            pytest.skip("No todos created for update test")
        
        # Given
        todo_id = self.created_todos[0]
        update_data = {
            "user_id": self.user_id,
            "title": "Updated Integration Test Todo",
            "description": "This todo has been updated",
            "completed": True,
            "priority": "low"
        }
        
        try:
            # When
            response = requests.put(
                f"{self.base_url}/todos/{todo_id}",
                json=update_data,
                headers={"Content-Type": "application/json"}
            )
            
            # Then
            assert response.status_code == 200
            data = response.json()
            assert data["title"] == update_data["title"]
            assert data["description"] == update_data["description"]
            assert data["completed"] is True
            assert data["priority"] == "low"
            assert data["todo_id"] == todo_id
            
        except requests.exceptions.ConnectionError:
            pytest.skip("SAM local server is not running")
    
    def test_update_todo_not_found(self):
        """存在しないTodoの更新テスト"""
        # Given
        nonexistent_id = "nonexistent-todo-id"
        update_data = {
            "user_id": self.user_id,
            "title": "This should not work"
        }
        
        try:
            # When
            response = requests.put(
                f"{self.base_url}/todos/{nonexistent_id}",
                json=update_data,
                headers={"Content-Type": "application/json"}
            )
            
            # Then
            assert response.status_code == 404
            data = response.json()
            assert "Todo not found" in data["error"]
            
        except requests.exceptions.ConnectionError:
            pytest.skip("SAM local server is not running")
    
    def test_delete_todo_success(self):
        """Todo削除の成功テスト"""
        # 前提条件: 削除用のTodoを作成
        todo_data = {
            "user_id": self.user_id,
            "title": "Todo to be deleted",
            "description": "This todo will be deleted in the test"
        }
        
        try:
            # 削除用のTodoを作成
            create_response = requests.post(
                f"{self.base_url}/todos",
                json=todo_data,
                headers={"Content-Type": "application/json"}
            )
            assert create_response.status_code == 201
            todo_id = create_response.json()["todo_id"]
            
            # When - Todo削除
            delete_response = requests.delete(
                f"{self.base_url}/todos/{todo_id}",
                params={"user_id": self.user_id}
            )
            
            # Then
            assert delete_response.status_code == 204
            assert delete_response.text == ""
            
            # 削除されたことを確認
            get_response = requests.get(f"{self.base_url}/todos", params={"user_id": self.user_id})
            assert get_response.status_code == 200
            todos = get_response.json()["todos"]
            todo_ids = [todo["todo_id"] for todo in todos]
            assert todo_id not in todo_ids
            
        except requests.exceptions.ConnectionError:
            pytest.skip("SAM local server is not running")
    
    def test_delete_todo_not_found(self):
        """存在しないTodoの削除テスト"""
        # Given
        nonexistent_id = "nonexistent-todo-id"
        
        try:
            # When
            response = requests.delete(
                f"{self.base_url}/todos/{nonexistent_id}",
                params={"user_id": self.user_id}
            )
            
            # Then
            assert response.status_code == 404
            data = response.json()
            assert "Todo not found" in data["error"]
            
        except requests.exceptions.ConnectionError:
            pytest.skip("SAM local server is not running")
    
    def test_cors_headers(self):
        """CORSヘッダーのテスト"""
        try:
            # When
            response = requests.get(f"{self.base_url}/todos", params={"user_id": self.user_id})
            
            # Then
            assert response.headers.get("Access-Control-Allow-Origin") == "*"
            assert "GET, POST, PUT, DELETE" in response.headers.get("Access-Control-Allow-Methods", "")
            
        except requests.exceptions.ConnectionError:
            pytest.skip("SAM local server is not running")
    
    def test_api_workflow(self):
        """APIワークフロー全体のテスト"""
        workflow_user = "workflow_test_user"
        
        try:
            # Step 1: 初期状態の確認（空のTodoリスト）
            response = requests.get(f"{self.base_url}/todos", params={"user_id": workflow_user})
            assert response.status_code == 200
            initial_todos = response.json()["todos"]
            initial_count = len(initial_todos)
            
            # Step 2: 新しいTodoを作成
            todo_data = {
                "user_id": workflow_user,
                "title": "Workflow Test Todo",
                "description": "Testing complete workflow",
                "priority": "medium"
            }
            create_response = requests.post(
                f"{self.base_url}/todos",
                json=todo_data,
                headers={"Content-Type": "application/json"}
            )
            assert create_response.status_code == 201
            created_todo = create_response.json()
            todo_id = created_todo["todo_id"]
            
            # Step 3: Todoリストの増加を確認
            response = requests.get(f"{self.base_url}/todos", params={"user_id": workflow_user})
            assert response.status_code == 200
            updated_todos = response.json()["todos"]
            assert len(updated_todos) == initial_count + 1
            
            # Step 4: 作成されたTodoを更新
            update_data = {
                "user_id": workflow_user,
                "title": "Updated Workflow Test Todo",
                "completed": True
            }
            update_response = requests.put(
                f"{self.base_url}/todos/{todo_id}",
                json=update_data,
                headers={"Content-Type": "application/json"}
            )
            assert update_response.status_code == 200
            updated_todo = update_response.json()
            assert updated_todo["title"] == "Updated Workflow Test Todo"
            assert updated_todo["completed"] is True
            
            # Step 5: 更新されたTodoを削除
            delete_response = requests.delete(
                f"{self.base_url}/todos/{todo_id}",
                params={"user_id": workflow_user}
            )
            assert delete_response.status_code == 204
            
            # Step 6: 削除後のTodoリストの確認
            response = requests.get(f"{self.base_url}/todos", params={"user_id": workflow_user})
            assert response.status_code == 200
            final_todos = response.json()["todos"]
            assert len(final_todos) == initial_count
            
        except requests.exceptions.ConnectionError:
            pytest.skip("SAM local server is not running")