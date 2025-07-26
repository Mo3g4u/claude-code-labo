<template>
  <div id="q-app">
    <!-- 認証されていない場合は認証画面を表示 -->
    <AuthForm 
      v-if="!isAuthenticated && !isLoading"
      @auth-success="handleAuthSuccess"
    />
    
    <!-- 認証されている場合はメインアプリを表示 -->
    <q-layout v-else-if="!isLoading" view="lHh Lpr lFf">
      <q-header elevated>
        <q-toolbar>
          <q-toolbar-title>
            Todo App
          </q-toolbar-title>
          
          <!-- ユーザー情報とログアウトボタン -->
          <div class="row items-center q-gutter-md">
            <span v-if="currentUser">{{ currentUser.email || currentUser.username }}</span>
            <q-btn
              flat
              dense
              icon="logout"
              @click="handleLogout"
              label="ログアウト"
            />
          </div>
        </q-toolbar>
      </q-header>

      <q-page-container>
        <q-page class="flex flex-center">
          <div class="q-pa-md" style="max-width: 600px; width: 100%;">
            <h4 class="q-mb-md">Todo List</h4>
            
            <!-- Add Todo Form -->
            <q-card class="q-mb-md">
              <q-card-section>
                <q-input
                  v-model="newTodo"
                  label="New Todo"
                  outlined
                  @keyup.enter="addTodo"
                >
                  <template v-slot:append>
                    <q-btn
                      round
                      dense
                      flat
                      icon="add"
                      @click="addTodo"
                    />
                  </template>
                </q-input>
              </q-card-section>
            </q-card>

            <!-- Todo List -->
            <q-list bordered separator>
              <q-item
                v-for="todo in todos"
                :key="todo.todo_id"
              >
                <q-item-section side>
                  <q-checkbox
                    v-model="todo.completed"
                    @update:model-value="toggleTodo(todo)"
                  />
                </q-item-section>
                <q-item-section>
                  <q-item-label :class="{ 'text-strike': todo.completed }">
                    {{ todo.title }}
                  </q-item-label>
                  <q-item-label caption v-if="todo.description">
                    {{ todo.description }}
                  </q-item-label>
                </q-item-section>
                <q-item-section side>
                  <q-btn
                    flat
                    round
                    dense
                    icon="delete"
                    @click.stop="deleteTodo(todo.todo_id)"
                  />
                </q-item-section>
              </q-item>
            </q-list>

            <!-- Empty State -->
            <div v-if="todos.length === 0" class="text-center q-pa-xl">
              <q-icon name="inbox" size="4rem" class="text-grey-5" />
              <p class="text-grey-6">No todos yet. Add one above!</p>
            </div>
          </div>
        </q-page>
      </q-page-container>
    </q-layout>
    
    <!-- ローディング画面 -->
    <div v-else class="loading-container">
      <q-spinner-dots size="50px" color="primary" />
      <div class="q-mt-md">読み込み中...</div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { useQuasar } from 'quasar'
import { todoApi } from './services/todoApi.js'
import authService from './services/authService.js'
import AuthForm from './components/AuthForm.vue'

export default {
  name: 'App',
  components: {
    AuthForm
  },
  setup() {
    const $q = useQuasar()
    const todos = ref([])
    const newTodo = ref('')
    const isAuthenticated = ref(false)
    const isLoading = ref(true)
    const currentUser = ref(null)

    const loadTodos = async () => {
      try {
        const response = await todoApi.getTodos()
        todos.value = response.todos
        console.log('Loaded todos:', response.todos)
      } catch (error) {
        console.error('Error loading todos:', error)
        $q.notify({
          type: 'negative',
          message: 'Failed to load todos'
        })
      }
    }

    const addTodo = async () => {
      if (!newTodo.value.trim()) return

      try {
        const todoData = {
          title: newTodo.value.trim(),
          description: '',
          priority: 'medium'
        }

        const newTodoItem = await todoApi.createTodo(todoData)
        todos.value.push(newTodoItem)
        newTodo.value = ''

        $q.notify({
          type: 'positive',
          message: 'Todo added successfully'
        })
      } catch (error) {
        console.error('Error adding todo:', error)
        $q.notify({
          type: 'negative',
          message: 'Failed to add todo'
        })
      }
    }

    const toggleTodo = async (todo) => {
      try {
        // v-modelで既に状態が更新されているので、再度反転させる必要はない
        await todoApi.updateTodo(todo.todo_id, {
          title: todo.title,
          description: todo.description,
          completed: todo.completed,
          priority: todo.priority
        })
        
        $q.notify({
          type: 'positive',
          message: todo.completed ? 'Todo completed!' : 'Todo reopened'
        })
      } catch (error) {
        // エラーが発生した場合は状態を元に戻す
        todo.completed = !todo.completed
        console.error('Error updating todo:', error)
        $q.notify({
          type: 'negative',
          message: 'Failed to update todo'
        })
      }
    }

    const deleteTodo = async (todoId) => {
      try {
        await todoApi.deleteTodo(todoId)
        todos.value = todos.value.filter(todo => todo.todo_id !== todoId)
        $q.notify({
          type: 'positive',
          message: 'Todo deleted successfully'
        })
      } catch (error) {
        console.error('Error deleting todo:', error)
        $q.notify({
          type: 'negative',
          message: 'Failed to delete todo'
        })
      }
    }

    // 認証成功時の処理
    const handleAuthSuccess = async (result) => {
      isAuthenticated.value = true
      currentUser.value = result.user
      
      // 認証成功後にTodoを読み込み
      await loadTodos()
      
      $q.notify({
        type: 'positive',
        message: 'ログインしました',
        position: 'top'
      })
    }

    // ログアウト処理
    const handleLogout = async () => {
      try {
        await authService.signOut()
        isAuthenticated.value = false
        currentUser.value = null
        todos.value = []
        
        $q.notify({
          type: 'positive',
          message: 'ログアウトしました',
          position: 'top'
        })
      } catch (error) {
        console.error('Logout error:', error)
        $q.notify({
          type: 'negative',
          message: 'ログアウトに失敗しました'
        })
      }
    }

    // 認証状態をチェック
    const checkAuthState = async () => {
      try {
        const session = await authService.getCurrentSession()
        if (session) {
          isAuthenticated.value = true
          currentUser.value = session.user
          await loadTodos()
        }
      } catch (error) {
        console.error('Auth check error:', error)
      } finally {
        isLoading.value = false
      }
    }

    // 認証状態変更リスナー
    const onAuthChange = (authenticated, user) => {
      isAuthenticated.value = authenticated
      currentUser.value = user
    }

    onMounted(async () => {
      // 認証状態リスナーを追加
      authService.addAuthListener(onAuthChange)
      
      // 初期認証状態をチェック
      await checkAuthState()
    })

    return {
      todos,
      newTodo,
      isAuthenticated,
      isLoading,
      currentUser,
      addTodo,
      toggleTodo,
      deleteTodo,
      handleAuthSuccess,
      handleLogout
    }
  }
}
</script>

<style>
.text-strike {
  text-decoration: line-through;
  opacity: 0.6;
}

.loading-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: #666;
}
</style>