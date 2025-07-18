import axios from 'axios'

const API_BASE_URL = 'http://127.0.0.1:3001'

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// レスポンスインターセプター
api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error)
    throw error
  }
)

export const todoApi = {
  // Todo一覧取得
  async getTodos(userId = 'user123') {
    try {
      const response = await api.get('/todos', {
        params: { user_id: userId }
      })
      return response.data
    } catch (error) {
      console.error('Error fetching todos:', error)
      throw error
    }
  },

  // Todo詳細取得
  async getTodo(todoId, userId = 'user123') {
    try {
      const response = await api.get(`/todos/${todoId}`, {
        params: { user_id: userId }
      })
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
        user_id: 'user123',
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
        user_id: 'user123',
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
  async deleteTodo(todoId, userId = 'user123') {
    try {
      await api.delete(`/todos/${todoId}`, {
        params: { user_id: userId }
      })
      return true
    } catch (error) {
      console.error('Error deleting todo:', error)
      throw error
    }
  }
}

export default todoApi