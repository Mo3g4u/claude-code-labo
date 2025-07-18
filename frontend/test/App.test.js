import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { Quasar } from 'quasar'
import App from '../src/App.vue'

// todoApi モックの設定
const mockTodoApi = {
  getTodos: vi.fn(),
  createTodo: vi.fn(),
  updateTodo: vi.fn(),
  deleteTodo: vi.fn()
}

vi.mock('../src/services/todoApi', () => mockTodoApi)

describe('App.vue', () => {
  let wrapper

  beforeEach(() => {
    // 各テストの前にmockをリセット
    vi.clearAllMocks()
    
    // デフォルトのmockレスポンスを設定
    mockTodoApi.getTodos.mockResolvedValue([])
    mockTodoApi.createTodo.mockResolvedValue({
      todo_id: 'test-id',
      title: 'Test Todo',
      description: '',
      completed: false,
      priority: 'medium',
      user_id: 'user123',
      created_at: '2025-01-01T00:00:00',
      updated_at: '2025-01-01T00:00:00'
    })
    mockTodoApi.updateTodo.mockResolvedValue({})
    mockTodoApi.deleteTodo.mockResolvedValue()
  })

  afterEach(() => {
    if (wrapper) {
      wrapper.unmount()
    }
  })

  const createWrapper = (options = {}) => {
    return mount(App, {
      global: {
        plugins: [
          [Quasar, {
            plugins: {
              Notify: {
                create: vi.fn()
              }
            }
          }]
        ],
        mocks: {
          $q: {
            notify: vi.fn()
          }
        },
        ...options.global
      },
      ...options
    })
  }

  it('コンポーネントが正しくレンダリングされる', async () => {
    // Given & When
    wrapper = createWrapper()
    await wrapper.vm.$nextTick()

    // Then
    expect(wrapper.find('h1').text()).toBe('Todo アプリ')
    expect(wrapper.find('input[placeholder="新しいTodoを入力"]').exists()).toBe(true)
    expect(wrapper.find('button').text()).toBe('追加')
  })

  it('初期状態でTodoリストが空である', async () => {
    // Given
    todoApi.getTodos.mockResolvedValue([])

    // When
    wrapper = createWrapper()
    await wrapper.vm.$nextTick()

    // Then
    expect(wrapper.vm.todos).toEqual([])
    expect(wrapper.find('.todo-item').exists()).toBe(false)
  })

  it('新しいTodoを追加できる', async () => {
    // Given
    const newTodo = {
      todo_id: 'new-todo-id',
      title: 'New Todo',
      description: '',
      completed: false,
      priority: 'medium',
      user_id: 'user123',
      created_at: '2025-01-01T00:00:00',
      updated_at: '2025-01-01T00:00:00'
    }
    
    todoApi.createTodo.mockResolvedValue(newTodo)
    todoApi.getTodos.mockResolvedValue([newTodo])

    wrapper = createWrapper()
    await wrapper.vm.$nextTick()

    // When
    await wrapper.find('input[placeholder="新しいTodoを入力"]').setValue('New Todo')
    await wrapper.find('button').trigger('click')
    await wrapper.vm.$nextTick()

    // Then
    expect(mockTodoApi.createTodo).toHaveBeenCalledWith({
      title: 'New Todo',
      description: '',
      priority: 'medium',
      user_id: 'user123'
    })
    expect(mockTodoApi.getTodos).toHaveBeenCalled()
  })

  it('空のタイトルでTodoを追加しようとするとエラーが表示される', async () => {
    // Given
    wrapper = createWrapper()
    await wrapper.vm.$nextTick()

    // When
    await wrapper.find('input[placeholder="新しいTodoを入力"]').setValue('')
    await wrapper.find('button').trigger('click')
    await wrapper.vm.$nextTick()

    // Then
    expect(mockTodoApi.createTodo).not.toHaveBeenCalled()
    expect(wrapper.vm.errorMessage).toBe('タイトルを入力してください')
  })

  it('Todoの完了状態を切り替えできる', async () => {
    // Given
    const todo = {
      todo_id: 'test-id',
      title: 'Test Todo',
      description: '',
      completed: false,
      priority: 'medium',
      user_id: 'user123',
      created_at: '2025-01-01T00:00:00',
      updated_at: '2025-01-01T00:00:00'
    }
    
    mockTodoApi.getTodos.mockResolvedValue([todo])
    mockTodoApi.updateTodo.mockResolvedValue({ ...todo, completed: true })

    wrapper = createWrapper()
    await wrapper.vm.$nextTick()

    // When
    await wrapper.vm.toggleTodo(todo)
    await wrapper.vm.$nextTick()

    // Then
    expect(mockTodoApi.updateTodo).toHaveBeenCalledWith('test-id', {
      ...todo,
      completed: true
    })
    expect(mockTodoApi.getTodos).toHaveBeenCalled()
  })

  it('Todoを削除できる', async () => {
    // Given
    const todo = {
      todo_id: 'test-id',
      title: 'Test Todo',
      description: '',
      completed: false,
      priority: 'medium',
      user_id: 'user123',
      created_at: '2025-01-01T00:00:00',
      updated_at: '2025-01-01T00:00:00'
    }
    
    mockTodoApi.getTodos.mockResolvedValue([todo])
    mockTodoApi.deleteTodo.mockResolvedValue()

    wrapper = createWrapper()
    await wrapper.vm.$nextTick()

    // When
    await wrapper.vm.deleteTodo(todo.todo_id)
    await wrapper.vm.$nextTick()

    // Then
    expect(mockTodoApi.deleteTodo).toHaveBeenCalledWith('test-id')
    expect(mockTodoApi.getTodos).toHaveBeenCalled()
  })

  it('APIエラーが発生した場合エラーメッセージが表示される', async () => {
    // Given
    mockTodoApi.getTodos.mockRejectedValue(new Error('API Error'))

    // When
    wrapper = createWrapper()
    await wrapper.vm.$nextTick()

    // Then
    expect(wrapper.vm.errorMessage).toBe('Todoの取得に失敗しました')
  })

  it('ローディング状態が正しく表示される', async () => {
    // Given
    let resolvePromise
    const loadingPromise = new Promise((resolve) => {
      resolvePromise = resolve
    })
    mockTodoApi.getTodos.mockReturnValue(loadingPromise)

    // When
    wrapper = createWrapper()
    await wrapper.vm.$nextTick()

    // Then - ローディング中
    expect(wrapper.vm.loading).toBe(true)

    // When - ローディング完了
    resolvePromise([])
    await wrapper.vm.$nextTick()

    // Then - ローディング完了
    expect(wrapper.vm.loading).toBe(false)
  })

  it('Todoリストが正しくレンダリングされる', async () => {
    // Given
    const todos = [
      {
        todo_id: 'todo-1',
        title: 'Todo 1',
        description: 'Description 1',
        completed: false,
        priority: 'high',
        user_id: 'user123',
        created_at: '2025-01-01T00:00:00',
        updated_at: '2025-01-01T00:00:00'
      },
      {
        todo_id: 'todo-2',
        title: 'Todo 2',
        description: 'Description 2',
        completed: true,
        priority: 'low',
        user_id: 'user123',
        created_at: '2025-01-01T00:00:00',
        updated_at: '2025-01-01T00:00:00'
      }
    ]

    mockTodoApi.getTodos.mockResolvedValue(todos)

    // When
    wrapper = createWrapper()
    await wrapper.vm.$nextTick()

    // Then
    expect(wrapper.vm.todos).toEqual(todos)
    expect(wrapper.findAll('.todo-item')).toHaveLength(2)
  })

  it('完了済みTodoが正しくスタイリングされる', async () => {
    // Given
    const completedTodo = {
      todo_id: 'todo-1',
      title: 'Completed Todo',
      description: '',
      completed: true,
      priority: 'medium',
      user_id: 'user123',
      created_at: '2025-01-01T00:00:00',
      updated_at: '2025-01-01T00:00:00'
    }

    mockTodoApi.getTodos.mockResolvedValue([completedTodo])

    // When
    wrapper = createWrapper()
    await wrapper.vm.$nextTick()

    // Then
    const todoItem = wrapper.find('.todo-item')
    expect(todoItem.classes()).toContain('completed')
  })
})