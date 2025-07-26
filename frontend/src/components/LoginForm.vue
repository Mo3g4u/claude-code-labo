<template>
  <q-card class="login-card">
    <q-card-section>
      <div class="text-h6 q-mb-md text-center">ログイン</div>
      
      <q-form @submit="handleLogin" class="q-gutter-md">
        <q-input
          v-model="formData.email"
          label="メールアドレス"
          type="email"
          outlined
          :rules="[val => !!val || 'メールアドレスを入力してください']"
          :loading="loading"
        />
        
        <q-input
          v-model="formData.password"
          label="パスワード"
          type="password"
          outlined
          :rules="[val => !!val || 'パスワードを入力してください']"
          :loading="loading"
        />
        
        <div class="row q-gutter-sm">
          <q-btn
            type="submit"
            color="primary"
            label="ログイン"
            class="col"
            :loading="loading"
          />
          <q-btn
            flat
            color="primary"
            label="新規登録"
            class="col"
            @click="$emit('switch-mode', 'signup')"
            :disable="loading"
          />
        </div>
      </q-form>
    </q-card-section>
  </q-card>
</template>

<script>
import { ref } from 'vue'
import { useQuasar } from 'quasar'
import authService from '../services/authService'

export default {
  name: 'LoginForm',
  emits: ['login-success', 'switch-mode'],
  setup(props, { emit }) {
    const $q = useQuasar()
    const loading = ref(false)
    
    const formData = ref({
      email: '',
      password: ''
    })

    const handleLogin = async () => {
      if (loading.value) return

      loading.value = true
      
      try {
        const result = await authService.signIn(formData.value.email, formData.value.password)
        
        $q.notify({
          type: 'positive',
          message: 'ログインしました'
        })
        
        emit('login-success', result)
        
        // フォームをリセット
        formData.value = {
          email: '',
          password: ''
        }
      } catch (error) {
        console.error('Login error:', error)
        
        let errorMessage = 'ログインに失敗しました'
        
        if (error.code === 'NotAuthorizedException') {
          errorMessage = 'メールアドレスまたはパスワードが正しくありません'
        } else if (error.code === 'UserNotConfirmedException') {
          errorMessage = 'メールアドレスの確認が必要です'
        } else if (error.message) {
          errorMessage = error.message
        }
        
        $q.notify({
          type: 'negative',
          message: errorMessage
        })
      } finally {
        loading.value = false
      }
    }

    return {
      formData,
      loading,
      handleLogin
    }
  }
}
</script>

<style scoped>
.login-card {
  width: 100%;
  max-width: 400px;
  margin: 0 auto;
}
</style>