<template>
  <div class="detail-page">
    <!-- 高德地图容器 -->
    <div id="amap-container"></div>

    <!-- 左上角：校园地图图标 -->
    <div class="map-mini-btn" @click="showCampusMap = true" title="查看校园地图">
      <span>🗺</span>
    </div>

    <!-- GPS 状态提示 -->
    <div v-if="gpsError" class="gps-tip">{{ gpsError }}</div>

    <!-- 转向指引步骤列表（导航激活后显示） -->
    <div v-if="steps.length > 0 && navigating" class="steps-panel" ref="stepsPanel">
      <div
        v-for="(step, i) in steps"
        :key="i"
        :class="['step-item', { active: i === currentStep }]"
        :ref="el => { if (el) stepRefs[i] = el }"
      >
        <span class="step-icon">{{ stepIcon(step.instruction) }}</span>
        <span class="step-text">{{ step.instruction }}</span>
        <span class="step-dist">{{ step.distance }}m</span>
      </div>
    </div>

    <!-- 底部信息栏 -->
    <div class="bottom-bar">
      <div class="loc-info" v-if="location">
        <strong>{{ location.name }}</strong>
        <span v-if="routeDistance" class="loc-meta">
          约 {{ routeDistance }}m · {{ routeDuration }}分钟
        </span>
      </div>
      <button
        v-if="!navigating"
        class="btn-primary"
        @click="startNavigation"
        :disabled="!routeReady"
      >
        ▶ 开始导航
      </button>
      <button v-else class="btn-primary btn-stop" @click="stopNavigation">
        ⏹ 结束导航
      </button>
    </div>

    <!-- 校园地图弹窗 -->
    <div v-if="showCampusMap" class="map-overlay" @click.self="showCampusMap = false">
      <div class="map-modal">
        <img
          v-if="!campusMapFailed"
          :src="campusMapUrl"
          alt="校园地图"
          class="campus-img"
          @error="campusMapFailed = true"
        />
        <div v-else class="campus-placeholder">暂无校园地图</div>
        <button class="close-btn" @click="showCampusMap = false">关闭</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onUnmounted, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api from '../api'

const route = useRoute()
const router = useRouter()

// ---- 数据 ----
const location = ref(null)
const showCampusMap = ref(false)
const campusMapFailed = ref(false)
const campusMapUrl = '/static/map/campus_map.jpg'
const gpsError = ref('')
const navigating = ref(false)
const routeReady = ref(false)
const routeDistance = ref(0)
const routeDuration = ref(0)
const steps = reactive([])
const currentStep = ref(0)
const stepRefs = reactive({})
const stepsPanel = ref(null)

// ---- 地图相关 ----
let map = null
let destMarker = null
let currentPosMarker = null
let walking = null
let geoWatcher = null
let routePath = []       // 路径坐标点
let lastSpokenStep = -1

const AMAP_KEY = '5e9cf78fff673e4b098e24a530926e78'
const AMAP_SECRET = '94b2fc14e7649625b0bb2ae9950eaa30'

// ==================== 生命周期 ====================
onMounted(async () => {
  const id = route.params.id
  try {
    const { data } = await api.get(`/admin/locations/${id}/`)
    location.value = data
  } catch {
    router.push('/nav')
    return
  }

  await loadAMap()
  initMap()
})

onUnmounted(() => {
  stopNavigation()
  try {
    if (map && document.getElementById('amap-container')) {
      map.destroy()
    }
  } catch (e) {
    console.error('[NavDetail] map.destroy error:', e)
  }
  map = null
})

// ==================== 高德地图加载 ====================
function loadAMap() {
  return new Promise((resolve) => {
    if (window.AMap) { resolve(); return }
    window._AMapSecurityConfig = { securityJsCode: AMAP_SECRET }
    const script = document.createElement('script')
    script.src = `https://webapi.amap.com/maps?v=2.0&key=${AMAP_KEY}&plugin=AMap.Walking,AMap.Geolocation`
    script.onload = resolve
    document.head.appendChild(script)
  })
}

// ==================== 初始化地图 + 路线 ====================
function initMap() {
  if (!location.value) return

  map = new window.AMap.Map('amap-container', {
    zoom: 17,
    center: [location.value.longitude, location.value.latitude],
    resizeEnable: true
  })

  // 目的地红色标记
  destMarker = new window.AMap.Marker({
    position: [location.value.longitude, location.value.latitude],
    title: location.value.name,
    map: map,
    label: {
      content: location.value.name,
      offset: new window.AMap.Pixel(0, -30)
    }
  })

  // GPS 定位 → 规划路线
  getCurrentPosition()
}

function getCurrentPosition() {
  window.AMap.plugin('AMap.Geolocation', () => {
    const geo = new window.AMap.Geolocation({
      enableHighAccuracy: true,
      timeout: 15000,
      maximumAge: 30000
    })
    geo.getCurrentPosition((status, result) => {
      if (status === 'complete' && result.position) {
        const lng = result.position.lng
        const lat = result.position.lat

        // 当前位置蓝色标记
        currentPosMarker = new window.AMap.Marker({
          position: [lng, lat],
          icon: new window.AMap.Icon({
            size: new window.AMap.Size(20, 20),
            image: 'https://webapi.amap.com/theme/v1.3/markers/n/mark_b.png'
          }),
          map: map
        })

        // 规划步行路线
        planRoute(lng, lat)
      } else {
        gpsError.value = '⚠ 无法获取当前位置，请检查定位权限'
      }
    })
  })
}

function planRoute(fromLng, fromLat) {
  if (!location.value) return
  const toLng = location.value.longitude
  const toLat = location.value.latitude

  walking = new window.AMap.Walking({ map: map })
  walking.search(
    [fromLng, fromLat],
    [toLng, toLat],
    (status, result) => {
      if (status === 'complete' && result.routes && result.routes.length > 0) {
        const route = result.routes[0]
        routeDistance.value = route.distance
        routeDuration.value = Math.ceil(route.duration / 60)

        // 收集路径坐标（用于后续位置匹配）
        routePath = []
        steps.length = 0
        route.steps.forEach((step, i) => {
          steps.push({
            instruction: step.instruction,
            distance: step.distance,
            road: step.road || '',
            path: step.path  // 该段路径坐标
          })
          if (step.path) {
            step.path.forEach(p => routePath.push(p))
          }
        })
        routeReady.value = true
      } else {
        gpsError.value = '⚠ 无法规划步行路线'
      }
    }
  )
}

// ==================== 导航控制 ====================
function startNavigation() {
  if (!routeReady.value) return
  navigating.value = true
  currentStep.value = 0
  lastSpokenStep = -1
  gpsError.value = ''

  // 播报第一段
  speakStep(0)

  // 持续跟踪位置
  window.AMap.plugin('AMap.Geolocation', () => {
    const geo = new window.AMap.Geolocation({
      enableHighAccuracy: true,
      timeout: 10000
    })
    geoWatcher = geo.watchPosition()
    window.AMap.event.addListener(geoWatcher, 'complete', onPositionUpdate)
  })
}

function stopNavigation() {
  navigating.value = false
  if (geoWatcher) {
    try { window.AMap.event.removeListener(geoWatcher, 'complete', onPositionUpdate) } catch (e) { console.error('[NavDetail] removeListener error:', e) }
    geoWatcher = null
  }
  try { window.speechSynthesis?.cancel() } catch (e) { console.error('[NavDetail] speech cancel error:', e) }
}

function onPositionUpdate(result) {
  if (!result.position || !navigating.value) return

  const myLng = result.position.lng
  const myLat = result.position.lat

  // 更新当前位置标记
  if (currentPosMarker) {
    currentPosMarker.setPosition([myLng, myLat])
  }

  // 匹配当前路段
  const newStep = findCurrentStep(myLng, myLat)
  if (newStep !== currentStep.value && newStep >= 0) {
    currentStep.value = newStep
    speakStep(newStep)
    scrollToStep(newStep)

    // 检查是否到达终点
    if (newStep >= steps.length - 1) {
      const dist = getDistance(myLng, myLat,
        location.value.longitude, location.value.latitude)
      if (dist < 30) {
        speak('已到达目的地 ' + location.value.name)
        setTimeout(() => stopNavigation(), 3000)
      }
    }
  }
}

// ==================== 位置计算 ====================
function findCurrentStep(lng, lat) {
  // 在 routePath 中找最近点，判断所在路段
  let minDist = Infinity
  let closestIdx = 0
  routePath.forEach((p, i) => {
    const d = getDistance(lng, lat, p.lng, p.lat)
    if (d < minDist) {
      minDist = d
      closestIdx = i
    }
  })

  // 根据最近点在 routePath 中的位置推算当前步骤
  let accumulated = 0
  for (let i = 0; i < steps.length; i++) {
    const stepLen = steps[i].path ? steps[i].path.length : 1
    if (closestIdx < accumulated + stepLen) return i
    accumulated += stepLen
  }
  return steps.length - 1
}

function getDistance(lng1, lat1, lng2, lat2) {
  const R = 6371000
  const dLat = (lat2 - lat1) * Math.PI / 180
  const dLng = (lng2 - lng1) * Math.PI / 180
  const a = Math.sin(dLat / 2) ** 2 +
    Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
    Math.sin(dLng / 2) ** 2
  return R * 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a))
}

// ==================== 语音播报 ====================
function speak(text) {
  if (!window.speechSynthesis) return
  window.speechSynthesis.cancel()
  const utter = new SpeechSynthesisUtterance(text)
  utter.lang = 'zh-CN'
  utter.rate = 1.0
  utter.pitch = 1.0
  window.speechSynthesis.speak(utter)
}

function speakStep(idx) {
  if (idx === lastSpokenStep) return
  lastSpokenStep = idx
  const step = steps[idx]
  if (!step) return

  let text = step.instruction
  if (idx === steps.length - 1) {
    text = '即将到达目的地 ' + (location.value?.name || '')
  }
  speak(text)
}

function scrollToStep(idx) {
  nextTick(() => {
    const el = stepRefs[idx]
    if (el && stepsPanel.value) {
      el.scrollIntoView({ behavior: 'smooth', block: 'center' })
    }
  })
}

// ==================== 图标映射 ====================
function stepIcon(instruction) {
  const text = instruction || ''
  if (text.includes('到达') || text.includes('终点') || text.includes('目的地')) return '🏁'
  if (text.includes('左转') || text.includes('向左')) return '↩'
  if (text.includes('右转') || text.includes('向右')) return '↪'
  if (text.includes('掉头') || text.includes('调头')) return '↩'
  if (text.includes('直行') || text.includes('沿')) return '⬆'
  if (text.includes('进入')) return '🚪'
  return '🚶'
}
</script>

<style scoped>
.detail-page {
  position: relative;
  width: 100%;
  height: 100vh;
  overflow: hidden;
}

/* ---- 地图 ---- */
#amap-container {
  width: 100%;
  height: 100%;
}

/* ---- 校园地图按钮 ---- */
.map-mini-btn {
  position: absolute;
  top: 16px;
  left: 16px;
  width: 44px;
  height: 44px;
  background: #fff;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 22px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.15);
  cursor: pointer;
  z-index: 10;
  transition: transform 0.15s;
}
.map-mini-btn:hover { transform: scale(1.1); }

/* ---- GPS 错误提示 ---- */
.gps-tip {
  position: absolute;
  top: 16px;
  left: 72px;
  right: 16px;
  background: rgba(255,255,255,0.92);
  padding: 8px 14px;
  border-radius: 8px;
  font-size: 12px;
  color: #e6a23c;
  z-index: 10;
  border: 1px solid var(--border);
}

/* ---- 步骤面板 ---- */
.steps-panel {
  position: absolute;
  bottom: 76px;
  left: 8px;
  right: 8px;
  max-height: 30vh;
  overflow-y: auto;
  background: rgba(255,255,255,0.96);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 8px 0;
  z-index: 5;
}
.step-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 14px;
  font-size: 13px;
  transition: background 0.2s;
}
.step-item.active {
  background: #ecf5ff;
  font-weight: 600;
}
.step-icon {
  width: 24px;
  text-align: center;
  flex-shrink: 0;
  font-size: 16px;
}
.step-text {
  flex: 1;
  color: #303133;
}
.step-dist {
  color: #909399;
  font-size: 12px;
  flex-shrink: 0;
}

/* ---- 底部栏 ---- */
.bottom-bar {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 12px 20px;
  background: var(--white);
  border-top: 1px solid var(--border);
  display: flex;
  justify-content: space-between;
  align-items: center;
  z-index: 10;
}
.loc-info strong {
  display: block;
  font-size: 15px;
}
.loc-meta {
  font-size: 12px;
  color: #909399;
}


/* ---- 校园地图弹窗 ---- */
.map-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0,0,0,0.6);
  z-index: 999;
  display: flex;
  align-items: center;
  justify-content: center;
}
.map-modal {
  background: var(--white);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 16px;
  width: 90%;
  max-width: 92vw;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  align-items: center;
}
.campus-img {
  width: 100%;
  max-height: 82vh;
  object-fit: contain;
  border-radius: 8px;
}
.campus-placeholder {
  padding: 60px 40px;
  color: #909399;
  font-size: 14px;
}
.close-btn {
  margin-top: 12px;
  padding: 8px 24px;
  background: #f5f7fa;
  border: 1px solid #dcdfe6;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
}


/* ---- end nav btn ---- */
.btn-stop { background: #DC2626; }
.btn-stop:hover { background: #B91C1C; }
</style>