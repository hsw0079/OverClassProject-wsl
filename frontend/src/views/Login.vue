<template>
  <div class="auth-page">
    <!-- 装饰背景 -->
    <div class="bg-shape bg-shape-1"></div>
    <div class="bg-shape bg-shape-2"></div>

    <div class="auth-card">
      <!-- Logo / 图标区 -->
      <div class="card-icon">
        <span class="icon-circle">🚗</span>
      </div>
      <h1>校园车辆进出管理</h1>
      <p class="subtitle">用户登录</p>

      <form @submit.prevent="handleLogin">
        <!-- 用户名 -->
        <div class="form-group">
          <label>用户名 / 手机号</label>
          <div class="input-wrap">
            <span class="input-icon">👤</span>
            <input
              v-model="username"
              type="text"
              placeholder="请输入用户名"
              autocomplete="username"
              required
              @focus="clearFieldError('username')"
            />
          </div>
        </div>

        <!-- 密码 -->
        <div class="form-group">
          <label>密码</label>
          <div class="input-wrap">
            <span class="input-icon">🔒</span>
            <input
              v-model="password"
              :type="showPwd ? 'text' : 'password'"
              placeholder="请输入密码"
              autocomplete="current-password"
              required
              @focus="clearFieldError('password')"
            />
            <span class="pwd-toggle" @click="showPwd = !showPwd">
              {{ showPwd ? '🙈' : '👁' }}
            </span>
          </div>
        </div>

        <!-- 记住我 -->
        <label class="remember-row">
          <input type="checkbox" v-model="rememberMe" />
          <span>记住用户名</span>
        </label>

        <!-- 错误提示 -->
        <transition name="fade">
          <div v-if="error" class="error-msg">
            <span class="error-icon">⚠️</span>
            <span>{{ error }}</span>
          </div>
        </transition>

        <!-- 登录按钮 -->
        <button type="submit" :disabled="loading" class="btn-login">
          <span v-if="loading" class="spinner"></span>
          <span>{{ loading ? '登录中...' : '登 录' }}</span>
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
const rememberMe = ref(false)
const error = ref('')
const loading = ref(false)

// 记住用户名
onMounted(() => {
  const saved = localStorage.getItem('remembered_username')
  if (saved) {
    username.value = saved
    rememberMe.value = true
  }
})

function clearFieldError() {
  if (error.value) error.value = ''
}

async function handleLogin() {
  console.log('[Login] button clicked, sending request to /api/auth/login/...')
  error.value = ''
  loading.value = true

  try {
    console.log('[Login] username:', username.value)
    await auth.login(username.value, password.value)
    console.log('[Login] success, redirecting to home')

    // 记住用户名
    if (rememberMe.value) {
      localStorage.setItem('remembered_username', username.value)
    } else {
      localStorage.removeItem('remembered_username')
    }

    router.push('/')
  } catch (e) {
    console.error('[Login] failed:', e)
    if (e.response) {
      const data = e.response.data
      if (typeof data === 'string') {
        error.value = data
      } else if (data.non_field_errors) {
        error.value = data.non_field_errors[0]
      } else if (data.detail) {
        error.value = data.detail
      } else {
        error.value = '用户名或密码错误，请重试'
      }
    } else if (e.code === 'ERR_NETWORK') {
      error.value = '无法连接服务器，请检查网络或确认后台已启动'
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
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 40%, #0f3460 100%);
  padding: 20px;
  position: relative;
  overflow: hidden;
}

/* 装饰背景 */
.bg-shape {
  position: absolute;
  border-radius: 50%;
  opacity: 0.08;
  pointer-events: none;
}
.bg-shape-1 {
  width: 400px; height: 400px;
  background: #667eea;
  top: -100px; right: -100px;
}
.bg-shape-2 {
  width: 300px; height: 300px;
  background: #764ba2;
  bottom: -80px; left: -80px;
}

.auth-card {
  position: relative;
  background: rgba(255,255,255,0.97);
  border-radius: 20px;
  padding: 40px 32px 32px;
  width: 100%;
  max-width: 400px;
  box-shadow: 0 24px 80px rgba(0,0,0,0.25);
  backdrop-filter: blur(10px);
}

/* 图标 */
.card-icon {
  text-align: center;
  margin-bottom: 8px;
}
.icon-circle {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 64px; height: 64px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea, #764ba2);
  font-size: 30px;
  box-shadow: 0 8px 24px rgba(102,126,234,0.35);
}

h1 {
  text-align: center;
  font-size: 20px;
  color: #1a1a2e;
  margin-bottom: 2px;
  font-weight: 700;
}
.subtitle {
  text-align: center;
  font-size: 13px;
  color: #909399;
  margin-bottom: 28px;
}

/* 表单 */
.form-group {
  margin-bottom: 18px;
}
.form-group label {
  display: block;
  font-size: 13px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 6px;
}

.input-wrap {
  position: relative;
  display: flex;
  align-items: center;
}
.input-icon {
  position: absolute;
  left: 12px;
  font-size: 16px;
  pointer-events: none;
  z-index: 1;
}
.input-wrap input {
  width: 100%;
  padding: 12px 12px 12px 38px;
  border: 1.5px solid #e4e7ed;
  border-radius: 10px;
  font-size: 15px;
  outline: none;
  transition: border-color 0.2s, box-shadow 0.2s;
  background: #fafbfc;
}
.input-wrap input:focus {
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102,126,234,0.12);
  background: #fff;
}
.pwd-toggle {
  position: absolute;
  right: 12px;
  cursor: pointer;
  font-size: 18px;
  user-select: none;
  opacity: 0.7;
}
.pwd-toggle:hover { opacity: 1; }

/* 记住我 */
.remember-row {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: #606266;
  cursor: pointer;
  margin-bottom: 4px;
  user-select: none;
}
.remember-row input[type="checkbox"] {
  accent-color: #667eea;
  width: 15px; height: 15px;
}

/* 错误 */
.error-msg {
  display: flex;
  align-items: center;
  gap: 8px;
  background: #fef0f0;
  color: #f56c6c;
  padding: 10px 14px;
  border-radius: 8px;
  font-size: 13px;
  margin-bottom: 12px;
  border: 1px solid #fde2e2;
}
.error-icon { font-size: 16px; flex-shrink: 0; }

/* 按钮 */
.btn-login {
  width: 100%;
  padding: 13px;
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: #fff;
  border: none;
  border-radius: 10px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  margin-top: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  transition: transform 0.15s, box-shadow 0.15s;
  box-shadow: 0 6px 20px rgba(102,126,234,0.3);
}
.btn-login:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 8px 28px rgba(102,126,234,0.4);
}
.btn-login:active:not(:disabled) {
  transform: translateY(0);
}
.btn-login:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

/* Spinner */
.spinner {
  width: 18px; height: 18px;
  border: 2px solid rgba(255,255,255,0.3);
  border-top-color: #fff;
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
}
@keyframes spin {
  to { transform: rotate(360deg); }
}

/* 底部链接 */
.switch-link {
  text-align: center;
  margin-top: 20px;
  font-size: 13px;
  color: #909399;
}
.switch-link a {
  color: #667eea;
  text-decoration: none;
  font-weight: 600;
}
.switch-link a:hover { text-decoration: underline; }

/* 过渡 */
.fade-enter-active, .fade-leave-active { transition: opacity 0.25s; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
</style>
