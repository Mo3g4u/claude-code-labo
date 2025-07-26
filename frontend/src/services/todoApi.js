import axios from 'axios'
import authService from './authService'

const API_BASE_URL = 'http://127.0.0.1:3000'

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// リクエストインターセプター - 認証トークンを自動で追加
api.interceptors.request.use(
  async (config) => {
    const token = await authService.getAccessToken()
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// レスポンスインターセプター
api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error)
    
    // 401エラーの場合はログアウト処理
    if (error.response?.status === 401) {
      authService.signOut()
    }
    
    throw error
  }
)

export const todoApi = {
  // Todo一覧取得
  async getTodos() {
    try {
      const response = await api.get('/todos')
      return response.data
    } catch (error) {
      console.error('Error fetching todos:', error)
      throw error
    }
  },

  // Todo詳細取得
  async getTodo(todoId) {
    try {
      const response = await api.get(`/todos/${todoId}`)
      return response.data
    } catch (error) {
      console.error('Error fetching todo:', error)
      throw error
    }
  },

  // Todo作成
  async createTodo(todoData) {
    try {
      const response = await api.post('/todos', {
        title: todoData.title,
        description: todoData.description || '',
        priority: todoData.priority || 'medium'
      })
      return response.data
    } catch (error) {
      console.error('Error creating todo:', error)
      throw error
    }
  },

  // Todo更新
  async updateTodo(todoId, todoData) {
    try {
      const response = await api.put(`/todos/${todoId}`, {
        title: todoData.title,
        description: todoData.description,
        completed: todoData.completed,
        priority: todoData.priority
      })
      return response.data
    } catch (error) {
      console.error('Error updating todo:', error)
      throw error
    }
  },

  // Todo削除
  async deleteTodo(todoId) {
    try {
      await api.delete(`/todos/${todoId}`)
      return true
    } catch (error) {
      console.error('Error deleting todo:', error)
      throw error
    }
  }
}

export default todoApi