<template>
  <div class="auth-container">
    <div class="auth-content">
      <div class="text-h4 text-center q-mb-lg">Todo App</div>
      
      <q-slide-transition>
        <LoginForm
          v-if="mode === 'login'"
          @login-success="handleAuthSuccess"
          @switch-mode="switchMode"
        />
      </q-slide-transition>
      
      <q-slide-transition>
        <SignUpForm
          v-if="mode === 'signup'"
          @signup-success="handleSignUpSuccess"
          @switch-mode="switchMode"
        />
      </q-slide-transition>
    </div>
  </div>
</template>

<script>
import { ref } from 'vue'
import LoginForm from './LoginForm.vue'
import SignUpForm from './SignUpForm.vue'

export default {
  name: 'AuthForm',
  components: {
    LoginForm,
    SignUpForm
  },
  emits: ['auth-success'],
  setup(props, { emit }) {
    const mode = ref('login')

    const switchMode = (newMode) => {
      mode.value = newMode
    }

    const handleAuthSuccess = (result) => {
      emit('auth-success', result)
    }

    const handleSignUpSuccess = (result) => {
      // サインアップ成功後は自動的にログイン画面に切り替わる
      console.log('Signup successful:', result)
    }

    return {
      mode,
      switchMode,
      handleAuthSuccess,
      handleSignUpSuccess
    }
  }
}
</script>

<style scoped>
.auth-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
}

.auth-content {
  width: 100%;
  max-width: 400px;
}

.auth-content .text-h4 {
  color: white;
  font-weight: 300;
  margin-bottom: 2rem;
}
</style>