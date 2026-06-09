<template>
  <div class="auth-page">
    <div class="auth-card">
      <h1>校园车辆进出管理</h1>
      <p class="subtitle">用户登录</p>
      <form @submit.prevent="handleLogin">
        <div class="form-group">
          <label>用户名 / 手机号</label>
          <input v-model="username" type="text" placeholder="请输入用户名" required />
        </div>
        <div class="form-group">
          <label>密码</label>
          <input v-model="password" type="password" placeholder="请输入密码" required />
        </div>
        <p v-if="error" class="error">{{ error }}</p>
        <button type="submit" :disabled="loading">{{ loading ? '登录中...' : '登录' }}</button>
      </form>
      <p class="switch-link">还没有账号？<router-link to="/register">立即注册</router-link></p>
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
const error = ref('')
const loading = ref(false)

async function handleLogin() {
  error.value = ''
  loading.value = true
  try {
    await auth.login(username.value, password.value)
    router.push('/')
  } catch (e) {
    error.value = e.response?.data?.non_field_errors?.[0] || '登录失败，请检查用户名和密码'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.auth-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
}
.auth-card {
  background: #fff;
  border-radius: 16px;
  padding: 36px 28px;
  width: 100%;
  max-width: 400px;
  box-shadow: 0 20px 60px rgba(0,0,0,0.15);
}
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