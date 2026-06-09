<template>
  <div class="qr-page">
    <div class="qr-card">
      <h3>通行二维码</h3>
      <div v-if="loading" class="qr-loading">加载中...</div>
      <img v-else-if="qrUrl" :src="qrUrl" alt="QR Code" class="qr-img" />
      <p v-if="error" class="qr-error">{{ error }}</p>
      <p v-if="expiresAt" class="expire">有效期至: {{ expiresAt }}</p>
      <p class="tip">凭此二维码可在有效时间内进出人行闸道</p>
      <button v-if="qrUrl" class="btn-save" @click="save">💾 保存页面</button>
      <router-link to="/" class="btn-back">← 返回首页</router-link>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import api from '../api'

const route = useRoute()
const qrUrl = ref('')
const expiresAt = ref('')
const loading = ref(true)
const error = ref('')

onMounted(async () => {
  const id = route.params.id

  // 1. 获取 QR 令牌信息（有效期等）
  try {
    const { data } = await api.get(`/appointments/${id}/qr-info/`)
    expiresAt.value = data.expires_at?.slice(0, 19).replace('T', ' ') || '-'
  } catch {
    error.value = '无法获取通行证信息'
    loading.value = false
    return
  }

  // 2. 用 axios（带 auth header）以 blob 方式请求 QR 图片
  try {
    const res = await api.get(`/appointments/${id}/qr/`, { responseType: 'blob' })
    const contentType = res.headers['content-type'] || ''

    if (contentType.includes('image/png')) {
      qrUrl.value = URL.createObjectURL(res.data)
    } else {
      // 后端返回了 JSON 错误（如未审批）
      const text = await res.data.text()
      try {
        const err = JSON.parse(text)
        error.value = err.error || '无法生成通行证'
      } catch {
        error.value = '无法生成通行证'
      }
    }
  } catch (e) {
    if (e.response?.status === 404) {
      error.value = '预约不存在'
    } else if (e.response?.status === 400) {
      error.value = '预约尚未通过审批，无法查看通行证'
    } else {
      error.value = '网络错误，请稍后重试'
    }
  } finally {
    loading.value = false
  }
})

function save() {
  if (!qrUrl.value) return
  const a = document.createElement('a')
  a.href = qrUrl.value
  a.download = '通行证_QR.png'
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
}
</script>

<style scoped>
.qr-page { min-height: 100vh; display: flex; align-items: center; justify-content: center; background: #f5f7fa; }
.qr-card { background: #fff; border-radius: 16px; padding: 32px; text-align: center; max-width: 360px; width: 90%; box-shadow: 0 8px 24px rgba(0,0,0,0.1); }
.qr-card h3 { margin-bottom: 20px; font-size: 18px; }
.qr-img { width: 240px; height: 240px; margin-bottom: 12px; image-rendering: pixelated; }
.qr-loading { padding: 80px 0; color: #909399; font-size: 14px; }
.qr-error { color: #f56c6c; font-size: 14px; margin-bottom: 12px; background: #fef0f0; padding: 10px; border-radius: 8px; }
.expire { font-size: 14px; color: #e6a23c; margin-bottom: 4px; }
.tip { font-size: 12px; color: #909399; margin-bottom: 20px; }
.btn-save { display: block; width: 100%; padding: 12px; background: #67c23a; color: #fff; border: none; border-radius: 8px; font-size: 15px; cursor: pointer; margin-bottom: 8px; }
.btn-back { display: block; padding: 10px; color: #667eea; text-decoration: none; font-size: 14px; }
</style>