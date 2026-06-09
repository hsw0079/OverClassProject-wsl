<template>
  <div class="nav-page">
    <header class="nav-header">
      <router-link to="/" class="back-btn">←</router-link>
      <h3>校内导航</h3>
    </header>
    <div class="nav-list">
      <div v-if="locations.length === 0" class="empty">暂无地点数据</div>
      <div v-for="loc in locations" :key="loc.id" class="nav-item" @click="goDetail(loc.id)">
        <span class="nav-icon">📍</span>
        <div class="nav-info">
          <strong>{{ loc.name }}</strong>
        </div>
        <span class="arrow">▶</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '../api'

const router = useRouter()
const locations = ref([])

onMounted(async () => {
  try { const { data } = await api.get('/admin/locations/'); locations.value = data.results || data } catch {}
})

function goDetail(id) { router.push('/nav/' + id) }
</script>

<style scoped>
.nav-page { max-width: 600px; margin: 0 auto; min-height: 100vh; background: #f5f7fa; }
.nav-header { display: flex; align-items: center; gap: 12px; padding: 14px 20px; background: linear-gradient(135deg, #667eea, #764ba2); color: #fff; }
.nav-header h3 { font-size: 17px; }
.back-btn { color: #fff; text-decoration: none; font-size: 20px; }

.nav-list { padding: 16px; }
.nav-item { display: flex; align-items: center; gap: 12px; padding: 14px; background: #fff; border-radius: 8px; margin-bottom: 8px; cursor: pointer; box-shadow: 0 1px 4px rgba(0,0,0,0.05); }
.nav-icon { font-size: 24px; }
.nav-info { flex: 1; }
.arrow { color: #c0c4cc; }
.empty { text-align: center; color: #c0c4cc; padding: 40px; }
</style>