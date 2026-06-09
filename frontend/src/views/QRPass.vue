<template>
  <div class="qr-page">
    <div class="qr-card">
      <h3>通行二维码</h3>
      <img v-if="qrUrl" :src="qrUrl" alt="QR Code" class="qr-img" />
      <p v-if="expiresAt" class="expire">有效期至: {{ expiresAt }}</p>
      <p class="tip">凭此二维码可在有效时间内进出人行闸道</p>
      <button class="btn-save" @click="save">💾 保存页面</button>
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

onMounted(async () => {
  const id = route.params.id
  try {
    const { data } = await api.get(`/appointments/${id}/qr-info/`)
    expiresAt.value = data.expires_at?.slice(0, 19).replace('T', ' ') || '-'
    qrUrl.value = `/api/appointments/${id}/qr/?t=${Date.now()}`
  } catch { alert('无法加载通行证') }
})

function save() {
  if (!qrUrl.value) return
  const a = document.createElement('a')
  a.href = qrUrl.value
  a.download = '通行证_QR.png'
  a.click()
}
</script>

<style scoped>
.qr-page { min-height: 100vh; display: flex; align-items: center; justify-content: center; background: #f5f7fa; }
.qr-card { background: #fff; border-radius: 16px; padding: 32px; text-align: center; max-width: 360px; width: 90%; box-shadow: 0 8px 24px rgba(0,0,0,0.1); }
.qr-card h3 { margin-bottom: 20px; font-size: 18px; }
.qr-img { width: 240px; height: 240px; margin-bottom: 12px; }
.expire { font-size: 14px; color: #e6a23c; margin-bottom: 4px; }
.tip { font-size: 12px; color: #909399; margin-bottom: 20px; }
.btn-save { display: block; width: 100%; padding: 12px; background: #67c23a; color: #fff; border: none; border-radius: 8px; font-size: 15px; cursor: pointer; margin-bottom: 8px; }
.btn-back { display: block; padding: 10px; color: #667eea; text-decoration: none; font-size: 14px; }
</style>