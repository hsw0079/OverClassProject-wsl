<template>
  <div class="qr-page">
    <div class="card" style="max-width:360px;width:90%;padding:32px;text-align:center">
      <h3 style="font-size:18px;font-weight:600;color:var(--carbon);margin-bottom:20px">通行二维码</h3>
      <div v-if="loading" style="padding:80px 0;color:var(--silver);font-size:14px">加载中...</div>
      <img v-else-if="qrUrl" :src="qrUrl" alt="QR Code" style="width:240px;height:240px;margin-bottom:12px" />
      <div v-if="error" style="color:#DC2626;font-size:14px;margin-bottom:12px;background:#FEF2F2;padding:10px;border-radius:4px">{{ error }}</div>
      <p v-if="expiresAt" style="font-size:14px;color:#B8860B;margin-bottom:4px">有效期至: {{ expiresAt }}</p>
      <p style="font-size:12px;color:var(--pewter);margin-bottom:20px">凭此二维码可在有效时间内进出人行闸道</p>
      <button v-if="qrUrl" class="btn-primary" style="width:100%" @click="save">保存通行证</button>
      <router-link to="/" style="display:block;margin-top:12px;font-size:14px;color:var(--pewter)">← 返回首页</router-link>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import api from '../api'

const route = useRoute()
const qrUrl = ref(''), expiresAt = ref(''), loading = ref(true), error = ref('')

onMounted(async () => {
  const id = route.params.id
  try { const { data } = await api.get(`/appointments/${id}/qr-info/`); expiresAt.value = data.expires_at?.slice(0, 19).replace('T', ' ') || '-' }
  catch { error.value = '无法获取通行证信息'; loading.value = false; return }
  try {
    const res = await api.get(`/appointments/${id}/qr/`, { responseType: 'blob' })
    if ((res.headers['content-type'] || '').includes('image/png')) { qrUrl.value = URL.createObjectURL(res.data) }
    else { const t = await res.data.text(); try { error.value = JSON.parse(t).error || '无法生成通行证' } catch { error.value = '无法生成通行证' } }
  } catch (e) {
    if (e.response?.status === 404) error.value = '预约不存在'
    else if (e.response?.status === 400) error.value = '预约尚未通过审批'
    else error.value = '网络错误，请稍后重试'
  } finally { loading.value = false }
})
function save() { if (!qrUrl.value) return; const a = document.createElement('a'); a.href = qrUrl.value; a.download = '通行证_QR.png'; document.body.appendChild(a); a.click(); document.body.removeChild(a) }
</script>

<style scoped>
.qr-page { min-height: 100vh; display: flex; align-items: center; justify-content: center; background: var(--ash); padding: 20px; }
</style>