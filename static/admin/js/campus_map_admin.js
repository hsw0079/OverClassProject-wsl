// 校内地点管理 - 高德地图集成 v2
window._campusMapMarker = null;
window._campusMapLng = null;
window._campusMapLat = null;

function openCampusMap(mode) {
  // 移除旧弹窗
  var old = document.getElementById('map-dialog-overlay');
  if (old) old.remove();

  // 等待 Amap 加载
  if (typeof AMap === 'undefined') { alert('高德地图正在加载，请稍候再试'); return; }

  var overlay = document.createElement('div');
  overlay.id = 'map-dialog-overlay';
  overlay.style.cssText = 'position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,0.5);z-index:99999;display:flex;align-items:center;justify-content:center;';

  var dialog = document.createElement('div');
  dialog.style.cssText = 'background:#fff;border-radius:8px;width:90%;max-width:800px;height:80%;display:flex;flex-direction:column;box-shadow:0 8px 32px rgba(0,0,0,0.3);';

  var header = document.createElement('div');
  header.style.cssText = 'padding:12px 16px;border-bottom:1px solid #eee;display:flex;justify-content:space-between;align-items:center;';
  header.innerHTML = '<strong style="font-size:16px">' + (mode === 'fuzzy' ? '模糊添加 - 点击地图选择位置' : '精准添加 - 当前位置') + '</strong>';
  var closeBtn = document.createElement('span');
  closeBtn.textContent = '\u2715';
  closeBtn.style.cssText = 'cursor:pointer;font-size:20px;color:#999;';
  closeBtn.onclick = function() { overlay.remove(); };
  header.appendChild(closeBtn);

  var mapContainer = document.createElement('div');
  mapContainer.id = 'map-dialog-container';
  mapContainer.style.cssText = 'flex:1;min-height:0;';

  var footer = document.createElement('div');
  footer.style.cssText = 'padding:12px 16px;border-top:1px solid #eee;display:flex;justify-content:space-between;align-items:center;';

  var coordDisplay = document.createElement('span');
  coordDisplay.style.cssText = 'font-size:13px;color:#666;';
  coordDisplay.textContent = mode === 'fuzzy' ? '点击地图选择位置' : '正在获取位置...';

  var actions = document.createElement('div');
  actions.style.cssText = 'display:flex;gap:8px;';

  if (mode === 'precise') {
    var locateBtn = document.createElement('button');
    locateBtn.textContent = '\uD83D\uDCCD 重新定位';
    locateBtn.style.cssText = 'padding:6px 16px;border:1px solid #ddd;border-radius:4px;background:#fff;cursor:pointer;';
    locateBtn.onclick = function() { doGeolocation(mapInst, coordDisplay); };
    actions.appendChild(locateBtn);
  }

  var addBtn2 = document.createElement('button');
  addBtn2.textContent = '\u2705 添加此位置';
  addBtn2.style.cssText = 'padding:6px 20px;border:none;border-radius:4px;background:#409eff;color:#fff;font-weight:600;cursor:pointer;';
  addBtn2.onclick = function() { doAddLocation(overlay); };
  actions.appendChild(addBtn2);

  footer.appendChild(coordDisplay);
  footer.appendChild(actions);

  dialog.appendChild(header);
  dialog.appendChild(mapContainer);
  dialog.appendChild(footer);
  overlay.appendChild(dialog);
  document.body.appendChild(overlay);

  // 初始化地图
  var mapInst = new AMap.Map('map-dialog-container', {
    zoom: 16,
    center: [116.397428, 39.90923],
    resizeEnable: true
  });

  if (mode === 'fuzzy') {
    mapInst.on('click', function(e) {
      window._campusMapLng = e.lnglat.getLng();
      window._campusMapLat = e.lnglat.getLat();
      coordDisplay.textContent = '已选择: ' + window._campusMapLng.toFixed(6) + ', ' + window._campusMapLat.toFixed(6);
      mapInst.clearMap();
      new AMap.Marker({ position: [window._campusMapLng, window._campusMapLat], map: mapInst });
    });
  } else {
    mapInst.setStatus({ dragEnable: false, zoomEnable: false });
    doGeolocation(mapInst, coordDisplay);
  }

  // 存储引用
  overlay._mapInst = mapInst;
}

function doGeolocation(mapInst, display) {
  if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(function(pos) {
      var lng = pos.coords.longitude, lat = pos.coords.latitude;
      mapInst.setCenter([lng, lat]);
      mapInst.clearMap();
      new AMap.Marker({ position: [lng, lat], map: mapInst });
      window._campusMapLng = lng; window._campusMapLat = lat;
      display.textContent = '当前位置: ' + lng.toFixed(6) + ', ' + lat.toFixed(6);
    }, function() { display.textContent = '无法获取位置，请检查定位权限'; });
  } else { display.textContent = '浏览器不支持定位'; }
}

function doAddLocation(overlay) {
  var lng = window._campusMapLng;
  var lat = window._campusMapLat;
  if (!lng || !lat) { alert('请先在地图上选择位置'); return; }
  var name = prompt('请输入地点名称：');
  if (!name || !name.trim()) return;

  // 获取 CSRF token
  var csrf = '';
  var cookies = document.cookie.split(';');
  for (var i = 0; i < cookies.length; i++) {
    var c = cookies[i].trim();
    if (c.startsWith('csrftoken=')) { csrf = c.substring(10); break; }
  }

  fetch('/api/admin/locations/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrf },
    body: JSON.stringify({ name: name.trim(), longitude: lng, latitude: lat })
  }).then(function(r) {
    if (r.ok) { overlay.remove(); location.reload(); }
    else { r.json().then(function(d) { alert('添加失败: ' + JSON.stringify(d)); }); }
  }).catch(function(e) { alert('请求失败: ' + e.message); });
}