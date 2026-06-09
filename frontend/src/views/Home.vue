<template>
  <div class="home-page">
    <!-- 顶部导航栏 -->
    <header class="top-bar">
      <div class="top-left">
        <span class="logo-icon">🚗</span>
        <h2>校园车辆进出管理</h2>
      </div>
      <div class="top-right">
        <span class="user-badge">👤 {{ user?.username || '用户' }}</span>
        <button class="btn-logout" @click="handleLogout">退出</button>
      </div>
    </header>

    <!-- 三窗口主体 -->
    <main class="main-grid">
      <!-- 窗口 1：预约申请 -->
      <section class="panel panel-form">
        <div class="panel-header panel-header-blue">
          <span>📝</span>
          <h3>预约申请</h3>
        </div>
        <div class="panel-body">
          <form @submit.prevent="submitAppointment">
            <div class="field">
              <label>访客姓名 *</label>
              <input v-model="form.visitor_name" placeholder="请输入姓名" required />
            </div>
            <div class="field">
              <label>访客电话 *</label>
              <input v-model="form.visitor_phone" placeholder="请输入手机号" required />
            </div>
            <div class="field">
              <label>车牌号 *</label>
              <input v-model="form.plate_number" placeholder="如：京A12345" required />
            </div>
            <div class="field">
              <label>被访人 *</label>
              <input v-model="form.host_name" placeholder="请输入被访人姓名" required />
            </div>
            <div class="field">
              <label>被访部门</label>
              <input v-model="form.host_department" placeholder="如：计算机学院" />
            </div>
            <div class="field">
              <label>预计进校时间 *</label>
              <input v-model="form.expected_time" type="datetime-local" required />
            </div>
            <div class="field">
              <label>事由 *</label>
              <textarea v-model="form.purpose" rows="2" placeholder="请简要说明来访事由" required></textarea>
            </div>
            <div class="field">
              <label>备注</label>
              <input v-model="form.remarks" placeholder="其他补充说明" />
            </div>

            <!-- 提交反馈 -->
            <transition name="fade">
              <div v-if="submitMsg" :class="['submit-feedback', submitOk ? 'ok' : 'fail']">
                {{ submitMsg }}
              </div>
            </transition>

            <button type="submit" :disabled="submitting" class="btn-submit">
              <span v-if="submitting" class="spinner"></span>
              {{ submitting ? '提交中...' : '提交预约' }}
            </button>
          </form>
        </div>
      </section>

      <!-- 窗口 2：申请状态 -->
      <section class="panel panel-status">
        <div class="panel-header panel-header-green">
          <span>📋</span>
          <h3>申请状态</h3>
          <span class="badge-count" v-if="appointments.length">{{ appointments.length }}</span>
        </div>
        <div class="panel-body scrollable">
          <div v-if="appointments.length === 0" class="empty-hint">
            🕐 暂无预约记录
          </div>
          <div
            v-for="apt in appointments"
            :key="apt.id"
            class="apt-item"
          >
            <div class="apt-top">
              <span :class="['status-tag', 'status-' + apt.status]">
                {{ apt.status_display || apt.status }}
              </span>
              <!-- QR 图标（仅已通过） -->
              <span
                v-if="apt.status === 'approved'"
                class="qr-icon"
                @click="$router.push('/qr/' + apt.id)"
                title="查看通行二维码"
              >📱</span>
            </div>
            <div class="apt-body">
              <div class="apt-row"><strong>{{ apt.visitor_name }}</strong> · {{ apt.plate_number }}</div>
              <div class="apt-row sub">被访：{{ apt.host_name }}</div>
              <div class="apt-row sub">时间：{{ formatTime(apt.expected_time) }}</div>
            </div>
          </div>
        </div>
      </section>

      <!-- 窗口 3：校内导航 -->
      <section class="panel panel-nav">
        <div class="panel-header panel-header-purple">
          <span>📍</span>
          <h3>校内导航</h3>
        </div>
        <div class="panel-body scrollable">
          <div v-if="locations.length === 0" class="empty-hint">
            🗺 暂无导航地点
          </div>
          <div
            v-for="loc in locations"
            :key="loc.id"
            class="nav-item"
            @click="$router.push('/nav/' + loc.id)"
          >
            <span class="nav-marker">📍</span>
            <span class="nav-name">{{ loc.name }}</span>
            <span class="nav-arrow">▶</span>
          </div>
        </div>
      </section>
    </main>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import api from '../api'

const router = useRouter()
const auth = useAuthStore()

// ---- 用户信息 ----
const user = ref(null)

// ---- 预约表单 ----
const form = reactive({
  visitor_name: '',
  visitor_phone: '',
  plate_number: '',
  host_name: '',
  host_department: '',
  expected_time: '',
  purpose: '',
  remarks: ''
})
const submitting = ref(false)
const submitMsg = ref('')
const submitOk = ref(true)

// ---- 预约列表 ----
const appointments = ref([])
const statusMap = { pending: '待审批', approved: '已通过', rejected: '已拒绝', arrived: '已到访', left: '已离开' }

// ---- 导航地点 ----
const locations = ref([])

// ==================== 生命周期 ====================
onMounted(async () => {
  await auth.init()
  await fetchUser()
  fetchAppointments()
  fetchLocations()
})

// ==================== 方法 ====================
async function fetchUser() {
  try {
    const { data } = await api.get('/auth/user/')
    user.value = data
  } catch { /* ignore */ }
}

async function fetchAppointments() {
  try {
    const { data } = await api.get('/appointments/')
    appointments.value = data.results || data || []
  } catch { appointments.value = [] }
}

async function fetchLocations() {
  try {
    const { data } = await api.get('/admin/locations/')
    locations.value = data.results || data || []
  } catch { locations.value = [] }
}

// ---- 提交预约 ----
async function submitAppointment() {
  submitMsg.value = ''
  submitting.value = true
  try {
    await api.post('/appointments/', {
      visitor_name: form.visitor_name.trim(),
      visitor_phone: form.visitor_phone.trim(),
      plate_number: form.plate_number.trim(),
      host_name: form.host_name.trim(),
      host_department: form.host_department.trim(),
      expected_time: form.expected_time,
      purpose: form.purpose.trim(),
      remarks: form.remarks.trim()
    })
    submitOk.value = true
    submitMsg.value = '✅ 预约提交成功！'
    // 重置表单
    Object.keys(form).forEach(k => form[k] = '')
    // 刷新列表
    await fetchAppointments()
    // 3 秒后清除提示
    setTimeout(() => { submitMsg.value = '' }, 3000)
  } catch (e) {
    submitOk.value = false
    const data = e.response?.data
    if (data) {
      const firstKey = Object.keys(data)[0]
      submitMsg.value = data[firstKey]?.[0] || '提交失败'
    } else {
      submitMsg.value = '网络错误，提交失败'
    }
  } finally {
    submitting.value = false
  }
}

// ---- 退出 ----
function handleLogout() {
  auth.logout()
  router.push('/login')
}

// ---- 格式化时间 ----
function formatTime(iso) {
  if (!iso) return '-'
  return iso.slice(0, 16).replace('T', ' ')
}
</script>

<style scoped>
/* ========== 整体布局 ========== */
.home-page {
  min-height: 100vh;
  background: #f0f2f5;
  display: flex;
  flex-direction: column;
}

/* ========== 顶部栏 ========== */
.top-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 24px;
  height: 56px;
  background: linear-gradient(135deg, #1a1a2e, #16213e);
  color: #fff;
  flex-shrink: 0;
}
.top-left {
  display: flex;
  align-items: center;
  gap: 10px;
}
.logo-icon { font-size: 24px; }
.top-left h2 { font-size: 16px; font-weight: 600; }
.top-right {
  display: flex;
  align-items: center;
  gap: 16px;
}
.user-badge { font-size: 13px; opacity: 0.9; }
.btn-logout {
  padding: 5px 14px;
  background: rgba(255,255,255,0.15);
  color: #fff;
  border: 1px solid rgba(255,255,255,0.25);
  border-radius: 6px;
  font-size: 12px;
  cursor: pointer;
}
.btn-logout:hover { background: rgba(255,255,255,0.25); }

/* ========== 三窗口网格 ========== */
.main-grid {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: 16px;
  padding: 16px;
  flex: 1;
  overflow: hidden;
}

@media (max-width: 900px) {
  .main-grid {
    grid-template-columns: 1fr;
    overflow-y: auto;
  }
}

/* ========== 面板通用 ========== */
.panel {
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.06);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}
.panel-header {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 14px 18px;
  font-size: 15px;
  font-weight: 600;
  color: #fff;
  flex-shrink: 0;
}
.panel-header-blue  { background: linear-gradient(135deg, #409eff, #337ecc); }
.panel-header-green { background: linear-gradient(135deg, #67c23a, #529b2e); }
.panel-header-purple{ background: linear-gradient(135deg, #a855f7, #7c3aed); }
.panel-header h3 { font-size: 14px; margin: 0; }
.badge-count {
  margin-left: auto;
  background: rgba(255,255,255,0.3);
  padding: 2px 8px;
  border-radius: 10px;
  font-size: 12px;
}

.panel-body {
  padding: 14px 18px;
  flex: 1;
  overflow-y: auto;
}
.panel-body.scrollable {
  padding: 8px 12px;
}

/* ========== 表单 ========== */
.field {
  margin-bottom: 10px;
}
.field label {
  display: block;
  font-size: 12px;
  font-weight: 600;
  color: #606266;
  margin-bottom: 3px;
}
.field input, .field textarea {
  width: 100%;
  padding: 8px 10px;
  border: 1px solid #dcdfe6;
  border-radius: 6px;
  font-size: 13px;
  outline: none;
  font-family: inherit;
  transition: border-color 0.2s;
}
.field input:focus, .field textarea:focus {
  border-color: #409eff;
}
.field textarea { resize: vertical; min-height: 48px; }

.btn-submit {
  width: 100%;
  padding: 10px;
  background: linear-gradient(135deg, #409eff, #337ecc);
  color: #fff;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  margin-top: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
}
.btn-submit:disabled { opacity: 0.6; cursor: not-allowed; }

.submit-feedback {
  padding: 8px 12px;
  border-radius: 6px;
  font-size: 13px;
  margin-bottom: 8px;
}
.submit-feedback.ok  { background: #f0f9eb; color: #67c23a; border: 1px solid #e1f3d8; }
.submit-feedback.fail{ background: #fef0f0; color: #f56c6c; border: 1px solid #fde2e2; }

/* ========== 状态列表 ========== */
.apt-item {
  padding: 12px;
  border: 1px solid #ebeef5;
  border-radius: 8px;
  margin-bottom: 8px;
  background: #fafbfc;
}
.apt-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 6px;
}
.status-tag {
  padding: 2px 10px;
  border-radius: 10px;
  font-size: 11px;
  font-weight: 600;
  color: #fff;
}
.status-pending  { background: #e6a23c; }
.status-approved { background: #67c23a; }
.status-rejected { background: #f56c6c; }
.status-arrived  { background: #409eff; }
.status-left     { background: #909399; }

.qr-icon {
  font-size: 22px;
  cursor: pointer;
  transition: transform 0.15s;
}
.qr-icon:hover { transform: scale(1.2); }

.apt-body { font-size: 12px; }
.apt-row { margin-bottom: 2px; }
.apt-row.sub { color: #909399; }

/* ========== 导航列表 ========== */
.nav-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px;
  border-radius: 8px;
  margin-bottom: 6px;
  background: #fafbfc;
  cursor: pointer;
  transition: background 0.15s;
  border: 1px solid #ebeef5;
}
.nav-item:hover { background: #f0f2f5; }
.nav-marker { font-size: 18px; }
.nav-name { flex: 1; font-size: 14px; font-weight: 500; }
.nav-arrow { color: #c0c4cc; font-size: 12px; }

/* ========== 空状态 ========== */
.empty-hint {
  text-align: center;
  color: #c0c4cc;
  font-size: 13px;
  padding: 24px 0;
}

/* ========== 通用 ========== */
.spinner {
  width: 14px; height: 14px;
  border: 2px solid rgba(255,255,255,0.3);
  border-top-color: #fff;
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }
.fade-enter-active, .fade-leave-active { transition: opacity 0.25s; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
</style>
