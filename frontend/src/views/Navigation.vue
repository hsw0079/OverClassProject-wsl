<template>
  <div class="nav-page">
    <!-- 顶部栏 -->
    <header class="nav-header">
      <router-link to="/" class="back-btn">←</router-link>
      <h3>校内导航</h3>
      <span class="header-count" v-if="locations.length">{{ locations.length }} 个地点</span>
    </header>

    <!-- 地点列表 -->
    <div class="nav-list">
      <!-- 空状态 -->
      <div v-if="locations.length === 0" class="empty-state">
        <div class="empty-icon">🗺️</div>
        <p class="empty-title">暂无导航地点</p>
        <p class="empty-desc">请管理员在后台添加校内地点标注</p>
      </div>

      <!-- 地点卡片 -->
      <div
        v-for="(loc, i) in locations"
        :key="loc.id"
        class="nav-item"
        @click="goDetail(loc.id)"
      >
        <span class="nav-num">{{ i + 1 }}</span>
        <div class="nav-info">
          <strong>{{ loc.name }}</strong>
          <span class="nav-coords" v-if="loc.longitude">
            {{ loc.longitude.toFixed(4) }}, {{ loc.latitude.toFixed(4) }}
          </span>
        </div>
        <span class="nav-arrow">▶</span>
      </div>
    </div>

    <!-- 底部提示 -->
    <footer class="nav-footer">
      <router-link to="/" class="footer-link">← 返回首页</router-link>
    </footer>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '../api'

const router = useRouter()
const locations = ref([])

onMounted(async () => {
  try {
    const { data } = await api.get('/admin/locations/')
    locations.value = data.results || data || []
  } catch {
    locations.value = []
  }
})

function goDetail(id) {
  router.push('/nav/' + id)
}
</script>

<style scoped>
.nav-page {
  max-width: 600px;
  margin: 0 auto;
  min-height: 100vh;
  background: #f5f7fa;
  display: flex;
  flex-direction: column;
}

/* ---- 顶部栏 ---- */
.nav-header {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 20px;
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: #fff;
  flex-shrink: 0;
}
.nav-header h3 {
  font-size: 17px;
  margin: 0;
  flex: 1;
}
.back-btn {
  color: #fff;
  text-decoration: none;
  font-size: 20px;
  line-height: 1;
}
.header-count {
  font-size: 12px;
  opacity: 0.8;
  background: rgba(255,255,255,0.2);
  padding: 3px 10px;
  border-radius: 10px;
}

/* ---- 列表 ---- */
.nav-list {
  padding: 16px;
  flex: 1;
}
.nav-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 16px;
  background: #fff;
  border-radius: 10px;
  margin-bottom: 8px;
  cursor: pointer;
  box-shadow: 0 1px 4px rgba(0,0,0,0.04);
  transition: transform 0.12s, box-shadow 0.12s;
}
.nav-item:hover {
  transform: translateY(-1px);
  box-shadow: 0 3px 12px rgba(0,0,0,0.08);
}
.nav-item:active {
  transform: translateY(0);
}
.nav-num {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 13px;
  font-weight: 700;
  flex-shrink: 0;
}
.nav-info {
  flex: 1;
  min-width: 0;
}
.nav-info strong {
  display: block;
  font-size: 15px;
  color: #303133;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.nav-coords {
  display: block;
  font-size: 11px;
  color: #c0c4cc;
  margin-top: 2px;
}
.nav-arrow {
  color: #c0c4cc;
  font-size: 12px;
  flex-shrink: 0;
}

/* ---- 空状态 ---- */
.empty-state {
  text-align: center;
  padding: 60px 20px;
}
.empty-icon {
  font-size: 56px;
  margin-bottom: 16px;
}
.empty-title {
  font-size: 16px;
  color: #606266;
  margin-bottom: 6px;
  font-weight: 600;
}
.empty-desc {
  font-size: 13px;
  color: #c0c4cc;
}

/* ---- 底部 ---- */
.nav-footer {
  padding: 12px 20px 20px;
  text-align: center;
  flex-shrink: 0;
}
.footer-link {
  color: #909399;
  text-decoration: none;
  font-size: 13px;
}
.footer-link:hover {
  color: #667eea;
}
</style>