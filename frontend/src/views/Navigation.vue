<template>
  <div class="nav-page">
    <header class="topbar">
      <router-link to="/" style="font-size:14px;color:var(--pewter);text-decoration:none">← 返回</router-link>
      <h3 style="font-size:16px;font-weight:600;color:var(--carbon)">校内导航</h3>
      <span v-if="locations.length" style="font-size:12px;color:var(--silver)">{{ locations.length }} 个地点</span>
    </header>
    <div class="nav-list">
      <div v-if="locations.length === 0" class="empty-state">
        <div style="font-size:48px;margin-bottom:12px">🗺️</div>
        <p style="color:var(--pewter);font-size:14px">暂无导航地点</p>
      </div>
      <div v-for="(loc, i) in locations" :key="loc.id" class="nav-item" @click="goDetail(loc.id)">
        <span class="nav-num">{{ i + 1 }}</span>
        <div class="nav-info"><strong>{{ loc.name }}</strong></div>
        <span class="nav-arrow">→</span>
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
onMounted(async () => { try { const { data } = await api.get('/admin/locations/'); locations.value = data.results || data || [] } catch { locations.value = [] } })
function goDetail(id) { router.push('/nav/' + id) }
</script>

<style scoped>
.nav-page { max-width: 600px; margin: 0 auto; min-height: 100vh; background: var(--white); }
.topbar { display: flex; align-items: center; justify-content: space-between; height: 52px; padding: 0 20px; border-bottom: 1px solid var(--border); }
.nav-list { padding: 16px; }
.nav-item { display: flex; align-items: center; gap: 12px; padding: 12px 14px; border: 1px solid var(--border); border-radius: var(--radius); margin-bottom: 8px; cursor: pointer; transition: var(--transition); }
.nav-item:hover { background: var(--ash); }
.nav-num { width: 28px; height: 28px; border-radius: 50%; background: var(--blue); color: #fff; display: flex; align-items: center; justify-content: center; font-size: 12px; font-weight: 600; flex-shrink: 0; }
.nav-info { flex: 1; }
.nav-info strong { font-size: 14px; color: var(--carbon); }
.nav-arrow { color: var(--silver); font-size: 12px; }
.empty-state { text-align: center; padding: 60px 20px; }
</style>