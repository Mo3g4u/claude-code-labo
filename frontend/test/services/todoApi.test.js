import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import axios from 'axios'
import { getTodos, createTodo, updateTodo, deleteTodo } from '../../src/services/todoApi'

// axios をモック
vi.mock('axios')
const mockedAxios = vi.mocked(axios)

describe('todoApi', () => {
  const mockTodo = {
    todo_id: 'test-id',
    title: 'Test Todo',
    description: 'Test Description',
    completed: false,
    priority: 'medium',
    user_id: 'user123',
    created_at: '2025-01-01T00:00:00',
    updated_at: '2025-01-01T00:00:00'
  }

  beforeEach(() => {
    vi.clearAllMocks()
  })

  afterEach(() => {
    vi.resetAllMocks()
  })

  describe('getTodos', () => {
    it('正常にTodoリストを取得できる', async () => {
      // Given
      const mockResponse = {
        data: {
          todos: [mockTodo],
          count: 1
        }
      }
      mockedAxios.get.mockResolvedValue(mockResponse)

      // When
      const result = await getTodos()

      // Then
      expect(mockedAxios.get).toHaveBeenCalledWith('http://localhost:3001/todos', {
        params: { user_id: 'user123' }
      })
      expect(result).toEqual([mockTodo])
    })

    it('APIエラーが発生した場合エラーをthrowする', async () => {
      // Given
      const mockError = new Error('API Error')
      mockedAxios.get.mockRejectedValue(mockError)

      // When & Then
      await expect(getTodos()).rejects.toThrow('API Error')
    })

    it('空のレスポンスの場合空配列を返す', async () => {
      // Given
      const mockResponse = {
        data: {
          todos: [],
          count: 0
        }
      }
      mockedAxios.get.mockResolvedValue(mockResponse)

      // When
      const result = await getTodos()

      // Then
      expect(result).toEqual([])
    })
  })

  describe('createTodo', () => {
    it('正常に新しいTodoを作成できる', async () => {
      // Given
      const newTodoData = {
        title: 'New Todo',
        description: 'New Description',
        priority: 'high',
        user_id: 'user123'
      }
      const mockResponse = {
        data: { ...mockTodo, ...newTodoData }
      }
      mockedAxios.post.mockResolvedValue(mockResponse)

      // When
      const result = await createTodo(newTodoData)

      // Then
      expect(mockedAxios.post).toHaveBeenCalledWith('http://localhost:3001/todos', newTodoData)
      expect(result).toEqual({ ...mockTodo, ...newTodoData })
    })

    it('APIエラーが発生した場合エラーをthrowする', async () => {
      // Given
      const newTodoData = {
        title: 'New Todo',
        user_id: 'user123'
      }
      const mockError = new Error('Create Error')
      mockedAxios.post.mockRejectedValue(mockError)

      // When & Then
      await expect(createTodo(newTodoData)).rejects.toThrow('Create Error')
    })

    it('バリデーションエラーが発生した場合エラーをthrowする', async () => {
      // Given
      const invalidTodoData = {
        description: 'No title',
        user_id: 'user123'
      }
      const mockError = {
        response: {
          status: 400,
          data: {
            error: 'Title is required'
          }
        }
      }
      mockedAxios.post.mockRejectedValue(mockError)

      // When & Then
      await expect(createTodo(invalidTodoData)).rejects.toEqual(mockError)
    })
  })

  describe('updateTodo', () => {
    it('正常にTodoを更新できる', async () => {
      // Given
      const todoId = 'test-id'
      const updateData = {
        title: 'Updated Todo',
        completed: true
      }
      const mockResponse = {
        data: { ...mockTodo, ...updateData }
      }
      mockedAxios.put.mockResolvedValue(mockResponse)

      // When
      const result = await updateTodo(todoId, updateData)

      // Then
      expect(mockedAxios.put).toHaveBeenCalledWith(`http://localhost:3001/todos/${todoId}`, updateData)
      expect(result).toEqual({ ...mockTodo, ...updateData })
    })

    it('存在しないTodoを更新しようとした場合エラーをthrowする', async () => {
      // Given
      const todoId = 'nonexistent-id'
      const updateData = { title: 'Updated Todo' }
      const mockError = {
        response: {
          status: 404,
          data: {
            error: 'Todo not found'
          }
        }
      }
      mockedAxios.put.mockRejectedValue(mockError)

      // When & Then
      await expect(updateTodo(todoId, updateData)).rejects.toEqual(mockError)
    })

    it('APIエラーが発生した場合エラーをthrowする', async () => {
      // Given
      const todoId = 'test-id'
      const updateData = { title: 'Updated Todo' }
      const mockError = new Error('Update Error')
      mockedAxios.put.mockRejectedValue(mockError)

      // When & Then
      await expect(updateTodo(todoId, updateData)).rejects.toThrow('Update Error')
    })
  })

  describe('deleteTodo', () => {
    it('正常にTodoを削除できる', async () => {
      // Given
      const todoId = 'test-id'
      const mockResponse = {
        status: 204,
        data: ''
      }
      mockedAxios.delete.mockResolvedValue(mockResponse)

      // When
      const result = await deleteTodo(todoId)

      // Then
      expect(mockedAxios.delete).toHaveBeenCalledWith(`http://localhost:3001/todos/${todoId}`, {
        params: { user_id: 'user123' }
      })
      expect(result).toBeUndefined()
    })

    it('存在しないTodoを削除しようとした場合エラーをthrowする', async () => {
      // Given
      const todoId = 'nonexistent-id'
      const mockError = {
        response: {
          status: 404,
          data: {
            error: 'Todo not found'
          }
        }
      }
      mockedAxios.delete.mockRejectedValue(mockError)

      // When & Then
      await expect(deleteTodo(todoId)).rejects.toEqual(mockError)
    })

    it('APIエラーが発生した場合エラーをthrowする', async () => {
      // Given
      const todoId = 'test-id'
      const mockError = new Error('Delete Error')
      mockedAxios.delete.mockRejectedValue(mockError)

      // When & Then
      await expect(deleteTodo(todoId)).rejects.toThrow('Delete Error')
    })
  })

  describe('HTTPステータスコード', () => {
    it('200レスポンスが正しく処理される', async () => {
      // Given
      const mockResponse = {
        data: {
          todos: [mockTodo],
          count: 1
        }
      }
      mockedAxios.get.mockResolvedValue(mockResponse)

      // When
      const result = await getTodos()

      // Then
      expect(result).toEqual([mockTodo])
    })

    it('201レスポンスが正しく処理される', async () => {
      // Given
      const newTodoData = {
        title: 'New Todo',
        user_id: 'user123'
      }
      const mockResponse = {
        data: { ...mockTodo, ...newTodoData }
      }
      mockedAxios.post.mockResolvedValue(mockResponse)

      // When
      const result = await createTodo(newTodoData)

      // Then
      expect(result).toEqual({ ...mockTodo, ...newTodoData })
    })

    it('204レスポンスが正しく処理される', async () => {
      // Given
      const todoId = 'test-id'
      const mockResponse = {
        status: 204,
        data: ''
      }
      mockedAxios.delete.mockResolvedValue(mockResponse)

      // When
      const result = await deleteTodo(todoId)

      // Then
      expect(result).toBeUndefined()
    })
  })

  describe('エラーハンドリング', () => {
    it('ネットワークエラーが正しく処理される', async () => {
      // Given
      const networkError = new Error('Network Error')
      networkError.code = 'ECONNREFUSED'
      mockedAxios.get.mockRejectedValue(networkError)

      // When & Then
      await expect(getTodos()).rejects.toThrow('Network Error')
    })

    it('タイムアウトエラーが正しく処理される', async () => {
      // Given
      const timeoutError = new Error('Timeout Error')
      timeoutError.code = 'ECONNABORTED'
      mockedAxios.get.mockRejectedValue(timeoutError)

      // When & Then
      await expect(getTodos()).rejects.toThrow('Timeout Error')
    })

    it('500エラーが正しく処理される', async () => {
      // Given
      const serverError = {
        response: {
          status: 500,
          data: {
            error: 'Internal Server Error'
          }
        }
      }
      mockedAxios.get.mockRejectedValue(serverError)

      // When & Then
      await expect(getTodos()).rejects.toEqual(serverError)
    })
  })
})