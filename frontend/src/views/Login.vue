<template>
  <div class="auth-page">
    <div class="auth-card">
      <!-- 标题 -->
      <h1 class="auth-title">校园车辆进出管理</h1>
      <p class="auth-sub">用户登录</p>

      <form @submit.prevent="handleLogin">
        <!-- 用户名 -->
        <div class="field">
          <label>用户名</label>
          <input
            v-model="username"
            type="text"
            class="input-line"
            placeholder="请输入用户名"
            autocomplete="username"
            required
          />
        </div>

        <!-- 密码 -->
        <div class="field">
          <label>密码</label>
          <div class="pwd-wrap">
            <input
              v-model="password"
              :type="showPwd ? 'text' : 'password'"
              class="input-line"
              placeholder="请输入密码"
              autocomplete="current-password"
              required
            />
            <span class="pwd-toggle" @click="showPwd = !showPwd">
              {{ showPwd ? '隐藏' : '显示' }}
            </span>
          </div>
        </div>

        <!-- 错误 -->
        <div v-if="error" class="error-msg">{{ error }}</div>

        <!-- 按钮 -->
        <button type="submit" :disabled="loading" class="btn-primary" style="width:100%;margin-top:24px">
          <span v-if="loading" class="spinner"></span>
          {{ loading ? '登录中...' : '登 录' }}
        </button>
      </form>

      <p class="switch-link">
        还没有账号？<router-link to="/register">立即注册</router-link>
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const auth = useAuthStore()
const username = ref('')
const password = ref('')
const showPwd = ref(false)
const error = ref('')
const loading = ref(false)

onMounted(() => {
  const saved = localStorage.getItem('remembered_username')
  if (saved) username.value = saved
})

async function handleLogin() {
  error.value = ''
  loading.value = true
  try {
    await auth.login(username.value, password.value)
    if (localStorage.getItem('remembered_username_ck') !== 'false') {
      localStorage.setItem('remembered_username', username.value)
    }
    router.push('/')
  } catch (e) {
    if (e.response) {
      const d = e.response.data
      error.value = d.non_field_errors?.[0] || d.detail || '用户名或密码错误'
    } else if (e.code === 'ERR_NETWORK') {
      error.value = '无法连接服务器，请确认后台已启动'
    } else {
      error.value = '登录失败，请稍后重试'
    }
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

.pwd-wrap { position: relative; }
.pwd-toggle { position: absolute; right: 0; top: 8px; font-size: 12px; color: var(--silver); cursor: pointer; user-select: none; }
.pwd-toggle:hover { color: var(--blue); }

.error-msg {
  background: #FEF2F2; color: #DC2626; padding: 10px 14px;
  border-radius: var(--radius); font-size: 13px; margin-top: 8px;
}

.switch-link { text-align: center; margin-top: 24px; font-size: 13px; color: var(--pewter); }
.switch-link a { color: var(--blue); font-weight: 500; }

.spinner { width: 16px; height: 16px; border: 2px solid rgba(255,255,255,.3); border-top-color: #fff; border-radius: 50%; animation: spin .6s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }
</style>