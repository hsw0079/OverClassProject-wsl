<template>
  <div class="auth-page">
    <div class="auth-card">
      <h1 class="auth-title">创建账号</h1>
      <p class="auth-sub">注册访客账号</p>

      <form @submit.prevent="handleRegister">
        <div class="field">
          <label>用户名</label>
          <input v-model="username" type="text" class="input-line" placeholder="请输入用户名" autocomplete="username" required />
        </div>
        <div class="field">
          <label>密码</label>
          <input v-model="password" type="password" class="input-line" placeholder="至少 6 位" required minlength="6" />
        </div>
        <div class="field">
          <label>确认密码</label>
          <input v-model="password2" type="password" class="input-line" placeholder="请再次输入密码" required />
        </div>

        <div v-if="error" class="error-msg">{{ error }}</div>

        <button type="submit" :disabled="loading" class="btn-primary" style="width:100%;margin-top:24px">
          <span v-if="loading" class="spinner"></span>
          {{ loading ? '注册中...' : '注 册' }}
        </button>
      </form>

      <p class="switch-link">
        已有账号？<router-link to="/login">去登录</router-link>
      </p>
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
  if (password.value !== password2.value) { error.value = '两次密码不一致'; return }
  loading.value = true
  try {
    await auth.register(username.value, password.value)
    router.push('/')
  } catch (e) {
    const d = e.response?.data
    error.value = typeof d === 'string' ? d : (d?.username?.[0] || d?.password?.[0] || '注册失败')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.auth-page {
  min-height: 100vh; display: flex; align-items: center; justify-content: center;
  background: var(--white); padding: 24px;
}
.auth-card {
  width: 100%; max-width: 380px;
  background: var(--white); border: 1px solid var(--border);
  border-radius: var(--radius); padding: 40px 32px 32px;
}
.auth-title { font-size: 20px; font-weight: 600; color: var(--carbon); text-align: center; }
.auth-sub { font-size: 13px; color: var(--pewter); text-align: center; margin: 6px 0 32px; }
.field { margin-bottom: 20px; }
.field label { display: block; font-size: 12px; font-weight: 600; color: var(--pewter); margin-bottom: 6px; text-transform: uppercase; letter-spacing: 0.5px; }
.error-msg { background: #FEF2F2; color: #DC2626; padding: 10px 14px; border-radius: var(--radius); font-size: 13px; margin-top: 8px; }
.switch-link { text-align: center; margin-top: 24px; font-size: 13px; color: var(--pewter); }
.switch-link a { color: var(--blue); font-weight: 500; }
.spinner { width: 16px; height: 16px; border: 2px solid rgba(255,255,255,.3); border-top-color: #fff; border-radius: 50%; animation: spin .6s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }
</style>