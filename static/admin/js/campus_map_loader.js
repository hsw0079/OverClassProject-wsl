// 校园地点 - 高德地图弹窗（统一版：可拖动模糊选点 + 右下角定位精确添加）
var _markerLng = null, _markerLat = null;

function openCampusMap() {
  var old = document.getElementById('map-dialog-overlay');
  if (old) old.remove();

  if (typeof AMap === 'undefined') { alert('高德地图尚在加载，请稍后重试'); return; }

  // 遮罩
  var overlay = document.createElement('div');
  overlay.id = 'map-dialog-overlay';
  overlay.style.cssText = 'position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,0.45);z-index:99999;display:flex;align-items:center;justify-content:center;';

  // 弹窗主体
  var dialog = document.createElement('div');
  dialog.style.cssText = 'position:relative;background:#fff;border-radius:8px;width:92%;max-width:850px;height:82%;display:flex;flex-direction:column;box-shadow:0 10px 40px rgba(0,0,0,0.3);';

  // 顶部栏
  var hdr = document.createElement('div');
  hdr.style.cssText = 'padding:12px 18px;border-bottom:1px solid #eee;display:flex;justify-content:space-between;align-items:center;flex-shrink:0;';
  hdr.innerHTML = '<strong style="font-size:15px">📍 添加校内地点</strong>';
  var cls = document.createElement('span');
  cls.textContent = '\u2715';
  cls.style.cssText = 'cursor:pointer;font-size:22px;color:#999;line-height:1;';
  cls.onclick = function() { overlay.remove(); };
  hdr.appendChild(cls);

  // 地图容器
  var mapDiv = document.createElement('div');
  mapDiv.id = 'map-dialog-map';
  mapDiv.style.cssText = 'flex:1;min-height:0;position:relative;';

  // 右下角定位按钮（叠在地图上）
  var locateBtn = document.createElement('div');
  locateBtn.innerHTML = '<span style="font-size:22px;">📍</span>';
  locateBtn.title = '定位到当前位置';
  locateBtn.style.cssText = 'position:absolute;bottom:20px;right:20px;width:44px;height:44px;background:#fff;border-radius:50%;display:flex;align-items:center;justify-content:center;box-shadow:0 2px 8px rgba(0,0,0,0.2);cursor:pointer;z-index:10;font-size:20px;';
  mapDiv.appendChild(locateBtn);

  // 底部栏
  var ftr = document.createElement('div');
  ftr.style.cssText = 'padding:10px 18px;border-top:1px solid #eee;display:flex;justify-content:space-between;align-items:center;flex-shrink:0;';

  var coord = document.createElement('span');
  coord.style.cssText = 'font-size:13px;color:#999;';
  coord.textContent = '点击地图选择位置，或点击右下角定位按钮';

  var addBtn = document.createElement('button');
  addBtn.textContent = '✅ 添加此位置';
  addBtn.style.cssText = 'padding:6px 22px;border:none;border-radius:4px;background:#409eff;color:#fff;font-weight:600;cursor:pointer;font-size:13px;';
  addBtn.onclick = function() {
    var lng = _markerLng, lat = _markerLat;
    if (!lng || !lat) { alert('请先在地图上选择位置（点击地图或使用定位）'); return; }
    var name = prompt('请输入地点名称：');
    if (!name || !name.trim()) return;
    var csrf = document.cookie.match(/csrftoken=([^;]+)/);
    fetch('/api/admin/locations/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrf ? csrf[1] : '' },
      body: JSON.stringify({ name: name.trim(), longitude: lng, latitude: lat })
    }).then(function(r) {
      if (r.ok) { overlay.remove(); location.reload(); }
      else { r.json().then(function(d) { alert('失败: ' + JSON.stringify(d)); }); }
    }).catch(function(e) { alert('请求失败: ' + e.message); });
  };

  ftr.appendChild(coord);
  ftr.appendChild(addBtn);

  dialog.appendChild(hdr);
  dialog.appendChild(mapDiv);
  dialog.appendChild(ftr);
  overlay.appendChild(dialog);
  document.body.appendChild(overlay);

  // 初始化高德地图（默认可拖动 = 模糊模式）
  var map = new AMap.Map('map-dialog-map', {
    zoom: 16,
    center: [116.397428, 39.90923],
    resizeEnable: true
  });

  // 放置标记点
  function placeMarker(lng, lat) {
    _markerLng = lng; _markerLat = lat;
    map.clearMap();
    new AMap.Marker({ position: [lng, lat], map: map });
    coord.textContent = '已选: 经度 ' + lng.toFixed(6) + ' , 纬度 ' + lat.toFixed(6);
    coord.style.color = '#409eff';
  }

  // 点击地图 → 模糊添加
  map.on('click', function(e) {
    placeMarker(e.lnglat.getLng(), e.lnglat.getLat());
  });

  // 右下角定位按钮 → 精确定位
  locateBtn.onclick = function() {
    coord.textContent = '正在获取位置...';
    coord.style.color = '#e6a23c';

    if (!navigator.geolocation) {
      coord.textContent = '浏览器不支持定位';
      coord.style.color = '#f56c6c';
      return;
    }

    navigator.geolocation.getCurrentPosition(
      function(pos) {
        var lng = pos.coords.longitude, lat = pos.coords.latitude;
        map.setCenter([lng, lat]);
        placeMarker(lng, lat);
        // 定位成功后改为不可拖动 2 秒再恢复（防误触）
        map.setStatus({ dragEnable: false });
        setTimeout(function() { map.setStatus({ dragEnable: true }); }, 3000);
      },
      function(err) {
        coord.textContent = '无法获取位置，请检查浏览器定位权限';
        coord.style.color = '#f56c6c';
      },
      { enableHighAccuracy: true, timeout: 15000 }
    );
  };
}