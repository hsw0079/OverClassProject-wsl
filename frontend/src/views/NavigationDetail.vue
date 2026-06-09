<template>
  <div class="detail-page">
    <div id="amap-container"></div>
    <div class="map-mini-btn" @click="showCampusMap = true">
      <span>🗺</span>
    </div>
    <div class="bottom-bar">
      <div class="loc-info" v-if="location">
        <strong>{{ location.name }}</strong>
        <span class="loc-addr">{{ location.name }}</span>
      </div>
      <button class="btn-nav" @click="startNavigation">▶ 开始导航</button>
    </div>

    <!-- 校园地图弹窗 -->
    <div v-if="showCampusMap" class="map-overlay" @click.self="showCampusMap = false">
      <div class="map-modal">
        <img src="/static/map/campus_map.jpg" alt="校园地图" class="campus-img"
             @error="onMapImgError" />
        <button class="close-btn" @click="showCampusMap = false">关闭</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api from '../api'

const route = useRoute()
const router = useRouter()
const location = ref(null)
const showCampusMap = ref(false)
let map = null
let walking = null
let currentMarker = null

const AMAP_KEY = '5e9cf78fff673e4b098e24a530926e78'           // 替换为实际 Key
const AMAP_SECRET = '94b2fc14e7649625b0bb2ae9950eaa30'     // 替换为实际安全密钥

onMounted(async () => {
  const id = route.params.id
  try {
    const { data } = await api.get(`/admin/locations/${id}/`)
    location.value = data
  } catch { router.push('/nav'); return }

  await loadAMap()
  initMap()
})

onUnmounted(() => {
  if (map) map.destroy()
})

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

function initMap() {
  if (!location.value) return
  map = new window.AMap.Map('amap-container', {
    zoom: 16,
    center: [location.value.longitude, location.value.latitude],
    resizeEnable: true
  })

  // 目的地标记
  currentMarker = new window.AMap.Marker({
    position: [location.value.longitude, location.value.latitude],
    title: location.value.name,
    map: map
  })

  // 定位当前位置
  window.AMap.plugin('AMap.Geolocation', function() {
    var geo = new window.AMap.Geolocation({ enableHighAccuracy: true, timeout: 10000 })
    geo.getCurrentPosition(function(status, result) {
      if (status === 'complete' && result.position) {
        var lng = result.position.lng, lat = result.position.lat
        new window.AMap.Marker({
          position: [lng, lat],
          icon: new window.AMap.Icon({ size: new window.AMap.Size(20,20), image: 'https://webapi.amap.com/theme/v1.3/markers/n/mark_b.png' }),
          map: map
        })
        // 规划路线
        walking = new window.AMap.Walking({ map: map })
        walking.search([lng, lat], [location.value.longitude, location.value.latitude], function(status, result) {
          // route drawn automatically
        })
      }
    })
  })
}

function startNavigation() {
  if (!location.value) return
  window.AMap.plugin('AMap.Geolocation', function() {
    var geo = new window.AMap.Geolocation({ enableHighAccuracy: true })
    geo.getCurrentPosition(function(status, result) {
      if (status === 'complete') {
        var to = location.value
        // 使用高德导航
        walking = new window.AMap.Walking({
          map: map,
          panel: 'panel',
          hideMarkers: false
        })
        walking.search(
          [result.position.lng, result.position.lat],
          [to.longitude, to.latitude],
          function(status, result) {
            if (status === 'complete') {
              // 语音播报需要 Walking 自带或额外集成
              if (window.AMap.WalkingRenderer) {
                // 导航开始
              }
            }
          }
        )
      } else {
        alert('无法获取当前位置，请检查定位权限')
      }
    })
  })
}

function onMapImgError() {
  // 校园地图加载失败
}
</script>

<style scoped>
.detail-page { position: relative; width: 100%; height: 100vh; }
#amap-container { width: 100%; height: 100%; }
.map-mini-btn {
  position: absolute; top: 16px; left: 16px;
  width: 44px; height: 44px; background: #fff; border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  font-size: 22px; box-shadow: 0 2px 8px rgba(0,0,0,0.15); cursor: pointer; z-index: 10;
}
.bottom-bar {
  position: absolute; bottom: 0; left: 0; right: 0;
  padding: 14px 20px; background: #fff; box-shadow: 0 -2px 8px rgba(0,0,0,0.08);
  display: flex; justify-content: space-between; align-items: center;
}
.loc-info strong { display: block; font-size: 15px; }
.loc-addr { font-size: 12px; color: #909399; }
.btn-nav {
  padding: 10px 24px; background: linear-gradient(135deg, #667eea, #764ba2);
  color: #fff; border: none; border-radius: 8px; font-size: 15px; font-weight: 600; cursor: pointer;
}
.map-overlay {
  position: fixed; top: 0; left: 0; width: 100%; height: 100%;
  background: rgba(0,0,0,0.6); z-index: 999;
  display: flex; align-items: center; justify-content: center;
}
.map-modal {
  background: #fff; border-radius: 12px; padding: 16px;
  width: 90%; max-width: 500px; max-height: 60vh;
  display: flex; flex-direction: column; align-items: center;
}
.campus-img { width: 100%; max-height: 50vh; object-fit: contain; border-radius: 8px; }
.close-btn { margin-top: 12px; padding: 8px 24px; background: #f5f7fa; border: 1px solid #dcdfe6; border-radius: 6px; cursor: pointer; }
</style>