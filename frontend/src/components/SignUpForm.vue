<template>
  <q-card class="signup-card">
    <q-card-section>
      <div class="text-h6 q-mb-md text-center">新規登録</div>
      
      <q-form @submit="handleSignUp" class="q-gutter-md">
        <q-input
          v-model="formData.name"
          label="名前"
          outlined
          :rules="[val => !!val || '名前を入力してください']"
          :loading="loading"
        />
        
        <q-input
          v-model="formData.email"
          label="メールアドレス"
          type="email"
          outlined
          :rules="[
            val => !!val || 'メールアドレスを入力してください',
            val => /.+@.+\..+/.test(val) || '有効なメールアドレスを入力してください'
          ]"
          :loading="loading"
        />
        
        <q-input
          v-model="formData.password"
          label="パスワード"
          type="password"
          outlined
          :rules="[
            val => !!val || 'パスワードを入力してください',
            val => val.length >= 8 || 'パスワードは8文字以上で入力してください'
          ]"
          :loading="loading"
        />
        
        <q-input
          v-model="formData.confirmPassword"
          label="パスワード（確認）"
          type="password"
          outlined
          :rules="[
            val => !!val || 'パスワード（確認）を入力してください',
            val => val === formData.password || 'パスワードが一致しません'
          ]"
          :loading="loading"
        />
        
        <div class="row q-gutter-sm">
          <q-btn
            type="submit"
            color="primary"
            label="登録"
            class="col"
            :loading="loading"
          />
          <q-btn
            flat
            color="primary"
            label="ログイン"
            class="col"
            @click="$emit('switch-mode', 'login')"
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
  name: 'SignUpForm',
  emits: ['signup-success', 'switch-mode'],
  setup(props, { emit }) {
    const $q = useQuasar()
    const loading = ref(false)
    
    const formData = ref({
      name: '',
      email: '',
      password: '',
      confirmPassword: ''
    })

    const handleSignUp = async () => {
      if (loading.value) return

      loading.value = true
      
      try {
        const result = await authService.signUp(
          formData.value.email,
          formData.value.password,
          formData.value.name
        )
        
        $q.notify({
          type: 'positive',
          message: '登録が完了しました。ログインしてください。'
        })
        
        emit('signup-success', result)
        emit('switch-mode', 'login')
        
        // フォームをリセット
        formData.value = {
          name: '',
          email: '',
          password: '',
          confirmPassword: ''
        }
      } catch (error) {
        console.error('Signup error:', error)
        
        let errorMessage = '登録に失敗しました'
        
        if (error.code === 'UsernameExistsException') {
          errorMessage = 'このメールアドレスは既に登録されています'
        } else if (error.code === 'InvalidPasswordException') {
          errorMessage = 'パスワードの形式が正しくありません'
        } else if (error.code === 'InvalidParameterException') {
          errorMessage = '入力内容に問題があります'
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
      handleSignUp
    }
  }
}
</script>

<style scoped>
.signup-card {
  width: 100%;
  max-width: 400px;
  margin: 0 auto;
}
</style>