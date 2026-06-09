<template>
  <div class="auth-page">
    <div class="auth-card">
      <h1>注册账号</h1>
      <p class="subtitle">创建您的访客账号</p>
      <form @submit.prevent="handleRegister">
        <div class="form-group">
          <label>用户名</label>
          <input v-model="username" type="text" placeholder="请输入用户名" required />
        </div>
        <div class="form-group">
          <label>密码</label>
          <input v-model="password" type="password" placeholder="至少6位" required minlength="6" />
        </div>
        <div class="form-group">
          <label>确认密码</label>
          <input v-model="password2" type="password" placeholder="请再次输入密码" required />
        </div>
        <p v-if="error" class="error">{{ error }}</p>
        <button type="submit" :disabled="loading">{{ loading ? '注册中...' : '注册' }}</button>
      </form>
      <p class="switch-link">已有账号？<router-link to="/login">去登录</router-link></p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const auth = useAuthStore()
const username = ref('')
const password = ref('')
const password2 = ref('')
const error = ref('')
const loading = ref(false)

async function handleRegister() {
  error.value = ''
  if (password.value !== password2.value) {
    error.value = '两次密码不一致'
    return
  }
  loading.value = true
  try {
    await auth.register(username.value, password.value)
    router.push('/')
  } catch (e) {
    const data = e.response?.data
    error.value = typeof data === 'string' ? data : (data?.username?.[0] || data?.password?.[0] || '注册失败')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.auth-page { min-height: 100vh; display: flex; align-items: center; justify-content: center; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 20px; }
.auth-card { background: #fff; border-radius: 16px; padding: 36px 28px; width: 100%; max-width: 400px; box-shadow: 0 20px 60px rgba(0,0,0,0.15); }
h1 { text-align: center; font-size: 20px; color: #303133; margin-bottom: 4px; }
.subtitle { text-align: center; font-size: 13px; color: #909399; margin-bottom: 24px; }
.form-group { margin-bottom: 16px; }
.form-group label { display: block; font-size: 13px; font-weight: 600; color: #606266; margin-bottom: 4px; }
.form-group input { width: 100%; padding: 10px 12px; border: 1px solid #dcdfe6; border-radius: 8px; font-size: 14px; outline: none; }
.form-group input:focus { border-color: #667eea; }
button { width: 100%; padding: 12px; background: linear-gradient(135deg, #667eea, #764ba2); color: #fff; border: none; border-radius: 8px; font-size: 16px; font-weight: 600; cursor: pointer; margin-top: 8px; }
button:disabled { opacity: 0.6; cursor: not-allowed; }
.error { background: #fef0f0; color: #f56c6c; padding: 8px 12px; border-radius: 6px; font-size: 13px; margin-bottom: 8px; }
.switch-link { text-align: center; margin-top: 16px; font-size: 13px; color: #909399; }
.switch-link a { color: #667eea; text-decoration: none; }
</style>