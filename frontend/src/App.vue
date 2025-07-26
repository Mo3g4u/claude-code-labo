<template>
  <div id="q-app">
    <!-- 認証されていない場合 -->
    <div v-if="!isAuthenticated" class="auth-container">
      <div class="auth-content">
        <h1>Todo App</h1>
        <q-card style="width: 350px;">
          <q-card-section>
            <div class="text-h6">ログイン</div>
          </q-card-section>
          <q-card-section>
            <q-input 
              v-model="email" 
              label="メールアドレス" 
              outlined 
            />
            <q-input 
              v-model="password" 
              label="パスワード" 
              type="password" 
              outlined 
              class="q-mt-md"
            />
            <q-btn 
              @click="testLogin" 
              color="primary" 
              label="ログイン" 
              class="q-mt-md full-width"
            />
          </q-card-section>
        </q-card>
      </div>
    </div>
    
    <!-- 認証されている場合 -->
    <q-layout v-else view="lHh Lpr lFf">
      <q-header elevated>
        <q-toolbar>
          <q-toolbar-title>
            Todo App
          </q-toolbar-title>
          <q-btn 
            flat 
            dense 
            icon="logout" 
            label="ログアウト"
            @click="testLogout"
          />
        </q-toolbar>
      </q-header>

      <q-page-container>
        <q-page class="flex flex-center">
          <div class="q-pa-md" style="max-width: 600px; width: 100%;">
            <h4>Todo List</h4>
            <p>ユーザー: {{ currentUser?.email || 'Unknown' }}</p>
            
            <!-- Todo作成フォーム -->
            <q-card class="q-mb-md">
              <q-card-section>
                <q-input
                  v-model="newTodo"
                  label="新しいTodo"
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

            <!-- Todo一覧 -->
            <div v-if="todos.length > 0">
              <q-list bordered separator>
                <q-item v-for="todo in todos" :key="todo.todo_id">
                  <q-item-section>
                    <q-item-label>{{ todo.title }}</q-item-label>
                    <q-item-label caption v-if="todo.description">
                      {{ todo.description }}
                    </q-item-label>
                  </q-item-section>
                  <q-item-section side>
                    <q-checkbox v-model="todo.completed" />
                  </q-item-section>
                </q-item>
              </q-list>
            </div>
            
            <!-- 空の状態 -->
            <div v-else class="text-center q-pa-xl">
              <q-icon name="inbox" size="4rem" class="text-grey-5" />
              <p class="text-grey-6">Todoがありません。上で追加してください！</p>
            </div>
            
            <!-- API テストボタン -->
            <div class="q-mt-md">
              <q-btn @click="testApi" color="secondary" label="API接続テスト" />
              <p v-if="apiStatus" class="q-mt-sm">{{ apiStatus }}</p>
            </div>
          </div>
        </q-page>
      </q-page-container>
    </q-layout>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'

// サービスのインポート
console.log('Importing services...')
import authService from './services/authService.js'
import { todoApi } from './services/todoApi.js'
console.log('Services import successful')

export default {
  name: 'App',
  setup() {
    const email = ref('')
    const password = ref('')
    const isAuthenticated = ref(false)
    const currentUser = ref(null)
    const newTodo = ref('')
    const todos = ref([])
    const apiStatus = ref('')
    
    const testLogin = async () => {
      console.log('Login button clicked')
      
      try {
        await authService.signIn(email.value, password.value)
        // 認証状態を手動で更新
        isAuthenticated.value = true
        currentUser.value = { email: email.value }
        console.log('Login successful, state updated')
        
        // ログイン後にTodoを読み込み
        await loadTodos()
      } catch (error) {
        console.error('Login error:', error)
      }
    }
    
    const testLogout = async () => {
      console.log('Logout button clicked')
      try {
        await authService.signOut()
        isAuthenticated.value = false
        currentUser.value = null
        todos.value = []
        email.value = ''
        password.value = ''
        console.log('Logout successful, state updated')
      } catch (error) {
        console.error('Logout error:', error)
      }
    }
    
    const loadTodos = async () => {
      try {
        apiStatus.value = 'Todo読み込み中...'
        const response = await todoApi.getTodos()
        todos.value = response.todos || []
        apiStatus.value = `Todo読み込み成功 (${todos.value.length}件)`
        console.log('Todos loaded:', todos.value)
      } catch (error) {
        console.error('Error loading todos:', error)
        apiStatus.value = 'Todo読み込みエラー: ' + error.message
      }
    }
    
    const addTodo = async () => {
      if (!newTodo.value.trim()) return
      
      try {
        apiStatus.value = 'Todo追加中...'
        const todoData = {
          title: newTodo.value.trim(),
          description: '',
          priority: 'medium'
        }
        
        const newTodoItem = await todoApi.createTodo(todoData)
        todos.value.push(newTodoItem)
        newTodo.value = ''
        apiStatus.value = 'Todo追加成功'
        console.log('Todo added:', newTodoItem)
      } catch (error) {
        console.error('Error adding todo:', error)
        apiStatus.value = 'Todo追加エラー: ' + error.message
      }
    }
    
    const testApi = async () => {
      try {
        apiStatus.value = 'API接続テスト中...'
        const response = await fetch('http://127.0.0.1:3000/todos')
        if (response.ok) {
          apiStatus.value = 'API接続成功！'
        } else {
          apiStatus.value = `API接続エラー: ${response.status}`
        }
      } catch (error) {
        console.error('API test error:', error)
        apiStatus.value = 'API接続失敗: ' + error.message
      }
    }
    
    onMounted(() => {
      console.log('App mounted successfully')
    })
    
    return {
      email,
      password,
      isAuthenticated,
      currentUser,
      newTodo,
      todos,
      apiStatus,
      testLogin,
      testLogout,
      addTodo,
      testApi
    }
  }
}
</script>

<style>
.auth-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
}

.auth-content {
  text-align: center;
}

.auth-content h1 {
  color: white;
  font-weight: 300;
  margin-bottom: 2rem;
}
</style>