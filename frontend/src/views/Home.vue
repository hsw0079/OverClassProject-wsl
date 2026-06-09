<template>
  <div class="home-page">
    <header class="topbar">
      <div class="top-left"><h2>校园车辆进出管理</h2></div>
      <div class="top-right">
        <span class="user-badge">{{ user?.username || '用户' }}</span>
        <button class="btn-secondary" style="height:32px;padding:0 14px;font-size:12px" @click="handleLogout">退出</button>
      </div>
    </header>
    <main class="main-grid">
      <!-- 预约申请 -->
      <section class="panel">
        <div class="panel-header"> 预约申请</div>
        <div class="panel-body">
          <form @submit.prevent="submitAppointment">
            <div class="field"><label>访客姓名 *</label><input v-model="form.visitor_name" class="input-line" placeholder="请输入姓名" required /></div>
            <div class="field"><label>访客电话 *</label><input v-model="form.visitor_phone" class="input-line" placeholder="请输入手机号" required /></div>
            <div class="field"><label>车牌号 *</label><input v-model="form.plate_number" class="input-line" placeholder="如：京A12345" required /></div>
            <div class="field"><label>被访人 *</label><input v-model="form.host_name" class="input-line" placeholder="请输入被访人姓名" required /></div>
            <div class="field"><label>被访部门</label><input v-model="form.host_department" class="input-line" placeholder="如：计算机学院" /></div>
            <div class="field"><label>预计进校时间 *</label><input v-model="form.expected_time" type="datetime-local" class="input-line" required /></div>
            <div class="field"><label>事由 *</label><input v-model="form.purpose" class="input-line" placeholder="请简要说明来访事由" required /></div>
            <div class="field"><label>备注</label><input v-model="form.remarks" class="input-line" placeholder="其他补充说明" /></div>
            <div v-if="submitMsg" :class="['feedback', submitOk ? 'fb-ok' : 'fb-fail']">{{ submitMsg }}</div>
            <button type="submit" :disabled="submitting" class="btn-primary" style="width:100%;margin-top:12px">
              <span v-if="submitting" class="spinner"></span>{{ submitting ? '提交中...' : '提交预约' }}
            </button>
          </form>
        </div>
      </section>
      <!-- 申请状态 -->
      <section class="panel">
        <div class="panel-header"> 申请状态<span v-if="appointments.length" class="count">{{ appointments.length }}</span></div>
        <div class="panel-body scrollable">
          <div v-if="appointments.length === 0" class="empty">暂无预约记录</div>
          <div v-for="apt in appointments" :key="apt.id" class="apt-item">
            <div class="apt-top">
              <span :class="['tag', 'tag-' + apt.status]">{{ apt.status_display || apt.status }}</span>
              <span v-if="apt.status === 'approved'" class="qr-btn" @click="$router.push('/qr/' + apt.id)">QR</span>
            </div>
            <div class="apt-info"><strong>{{ apt.visitor_name }}</strong> · {{ apt.plate_number }}<div class="apt-sub">被访：{{ apt.host_name }} · {{ formatTime(apt.expected_time) }}</div></div>
          </div>
        </div>
      </section>
      <!-- 校内导航 -->
      <section class="panel">
        <div class="panel-header"> 校内导航</div>
        <div class="panel-body scrollable">
          <div v-if="locations.length === 0" class="empty">暂无导航地点</div>
          <div v-for="loc in locations" :key="loc.id" class="nav-item" @click="$router.push('/nav/' + loc.id)">
            <span class="nav-dot"></span><span class="nav-name">{{ loc.name }}</span><span class="nav-arrow">→</span>
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
const user = ref(null)
const form = reactive({ visitor_name:'', visitor_phone:'', plate_number:'', host_name:'', host_department:'', expected_time:'', purpose:'', remarks:'' })
const submitting = ref(false), submitMsg = ref(''), submitOk = ref(true)
const appointments = ref([]), locations = ref([])

onMounted(async () => {
  try { const { data } = await api.get('/auth/user/'); user.value = data } catch (e) { console.error('[Home] fetch user failed:', e) }
  fetchAppointments(); fetchLocations()
})
async function fetchAppointments() { try { const { data } = await api.get('/appointments/'); appointments.value = data.results || data || [] } catch (e) { console.error('[Home] fetch appointments failed:', e); appointments.value = [] } }
async function fetchLocations() { try { const { data } = await api.get('/admin/locations/'); locations.value = data.results || data || [] } catch (e) { console.error('[Home] fetch locations failed:', e); locations.value = [] } }
async function submitAppointment() {
  submitMsg.value = ''; submitting.value = true
  try {
    await api.post('/appointments/', { visitor_name:form.visitor_name.trim(), visitor_phone:form.visitor_phone.trim(), plate_number:form.plate_number.trim(), host_name:form.host_name.trim(), host_department:form.host_department.trim(), expected_time:form.expected_time, purpose:form.purpose.trim(), remarks:form.remarks.trim() })
    submitOk.value = true; submitMsg.value = '预约提交成功'
    Object.keys(form).forEach(k => form[k] = '')
    await fetchAppointments(); setTimeout(() => { submitMsg.value = '' }, 3000)
  } catch (e) { submitOk.value = false; const d = e.response?.data; submitMsg.value = d ? (Object.values(d)[0]?.[0] || '提交失败') : '网络错误' }
  finally { submitting.value = false }
}
function handleLogout() { auth.logout(); router.push('/login') }
function formatTime(iso) { return iso ? iso.slice(0, 16).replace('T', ' ') : '-' }
</script>

<style scoped>
.home-page { min-height: 100vh; background: var(--ash); display: flex; flex-direction: column; }
.topbar { display: flex; justify-content: space-between; align-items: center; height: 52px; padding: 0 24px; background: var(--white); border-bottom: 1px solid var(--border); }
.top-left h2 { font-size: 16px; font-weight: 600; color: var(--carbon); }
.top-right { display: flex; align-items: center; gap: 16px; }
.user-badge { font-size: 13px; color: var(--pewter); }
.main-grid { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 16px; padding: 16px; flex: 1; overflow: hidden; }
@media (max-width: 900px) { .main-grid { grid-template-columns: 1fr; overflow-y: auto; } }
.panel { background: var(--white); border: 1px solid var(--border); border-radius: var(--radius); display: flex; flex-direction: column; overflow: hidden; }
.panel-header { padding: 12px 16px; font-size: 13px; font-weight: 600; color: var(--carbon); border-bottom: 1px solid var(--border); background: var(--ash); display: flex; align-items: center; gap: 6px; }
.count { margin-left: auto; font-size: 11px; color: var(--pewter); background: var(--white); padding: 1px 8px; border-radius: 10px; border: 1px solid var(--border); }
.panel-body { padding: 14px 16px; flex: 1; overflow-y: auto; }
.panel-body.scrollable { padding: 8px 12px; }
.field { margin-bottom: 10px; }
.field label { display: block; font-size: 11px; font-weight: 600; color: var(--pewter); margin-bottom: 2px; text-transform: uppercase; letter-spacing: 0.3px; }
.feedback { padding: 8px 12px; border-radius: var(--radius); font-size: 12px; margin-bottom: 4px; }
.fb-ok { background: #E8F5E9; color: #2E7D32; }
.fb-fail { background: #FEF2F2; color: #DC2626; }
.apt-item { padding: 10px 12px; border: 1px solid var(--border); border-radius: var(--radius); margin-bottom: 8px; }
.apt-top { display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px; }
.qr-btn { font-size: 11px; font-weight: 600; color: var(--blue); cursor: pointer; padding: 2px 8px; border: 1px solid var(--blue); border-radius: var(--radius); }
.qr-btn:hover { background: var(--blue); color: #fff; }
.apt-info { font-size: 13px; }
.apt-sub { font-size: 12px; color: var(--pewter); margin-top: 2px; }
.nav-item { display: flex; align-items: center; gap: 10px; padding: 10px 12px; border: 1px solid var(--border); border-radius: var(--radius); margin-bottom: 6px; cursor: pointer; transition: var(--transition); }
.nav-item:hover { background: var(--ash); }
.nav-dot { width: 8px; height: 8px; border-radius: 50%; background: var(--blue); flex-shrink: 0; }
.nav-name { flex: 1; font-size: 13px; font-weight: 500; color: var(--carbon); }
.nav-arrow { color: var(--silver); font-size: 12px; }
.empty { text-align: center; color: var(--silver); font-size: 13px; padding: 24px 0; }
.spinner { width: 14px; height: 14px; border: 2px solid rgba(255,255,255,.3); border-top-color: #fff; border-radius: 50%; animation: spin .6s linear infinite; display: inline-block; }
@keyframes spin { to { transform: rotate(360deg); } }
</style>