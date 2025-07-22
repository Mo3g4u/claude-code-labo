import { describe, it, expect, beforeEach } from 'vitest'
import todoApi from '../../src/services/todoApi.js'

// 統合テスト用のベースURL設定
const API_BASE_URL = process.env.VITE_API_BASE_URL || 'http://localhost:3001'

describe('API Integration Tests', () => {
  beforeEach(() => {
    // APIのベースURLを設定
    todoApi.defaults.baseURL = API_BASE_URL
  })

  it('should get todos from API', async () => {
    try {
      const response = await todoApi.get('/todos?user_id=test_user')
      expect(response.status).toBe(200)
      expect(response.data).toHaveProperty('todos')
      expect(Array.isArray(response.data.todos)).toBe(true)
    } catch (error) {
      // API が起動していない場合はスキップ
      if (error.code === 'ECONNREFUSED') {
        console.warn('API server is not running, skipping integration test')
        return
      }
      throw error
    }
  })

  it('should create a new todo via API', async () => {
    const newTodo = {
      title: 'Integration Test Todo',
      description: 'This is a test todo for integration testing',
      priority: 'high'
    }

    try {
      const response = await todoApi.post('/todos', {
        ...newTodo,
        user_id: 'test_user'
      })
      
      expect(response.status).toBe(201)
      expect(response.data).toHaveProperty('todo_id')
      expect(response.data.title).toBe(newTodo.title)
      expect(response.data.completed).toBe(false)
    } catch (error) {
      if (error.code === 'ECONNREFUSED') {
        console.warn('API server is not running, skipping integration test')
        return
      }
      throw error
    }
  })

  it('should handle API errors gracefully', async () => {
    try {
      // 無効なエンドポイントにアクセス
      await todoApi.get('/invalid-endpoint')
    } catch (error) {
      if (error.code === 'ECONNREFUSED') {
        console.warn('API server is not running, skipping integration test')
        return
      }
      // APIエラーのレスポンスを確認
      expect(error.response?.status).toBeGreaterThanOrEqual(400)
    }
  })
})