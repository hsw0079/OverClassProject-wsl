// 校园地点 - 高德地图弹窗（Tesla 风格）
var _markerLng = null, _markerLat = null;

function openCampusMap() {
  var old = document.getElementById('map-dialog-overlay');
  if (old) old.remove();
  if (typeof AMap === 'undefined') { alert('高德地图尚在加载，请稍后重试'); return; }

  // 遮罩
  var overlay = document.createElement('div');
  overlay.id = 'map-dialog-overlay';
  overlay.style.cssText = 'position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,0.4);z-index:99999;display:flex;align-items:center;justify-content:center;';

  // 弹窗
  var dialog = document.createElement('div');
  dialog.style.cssText = 'position:relative;background:#fff;border:1px solid #E5E7EB;border-radius:4px;width:92%;max-width:850px;height:82%;display:flex;flex-direction:column;';

  // 顶部栏
  var hdr = document.createElement('div');
  hdr.style.cssText = 'padding:12px 18px;border-bottom:1px solid #E5E7EB;display:flex;justify-content:space-between;align-items:center;flex-shrink:0;background:#F4F4F4;';
  hdr.innerHTML = '<strong style="font-size:13px;color:#171A20">添加校内地点</strong>';
  var cls = document.createElement('span');
  cls.textContent = '\u2715';
  cls.style.cssText = 'cursor:pointer;font-size:18px;color:#8E8E8E;line-height:1;';
  cls.onclick = function() { overlay.remove(); };
  hdr.appendChild(cls);

  // 地图
  var mapDiv = document.createElement('div');
  mapDiv.id = 'map-dialog-map';
  mapDiv.style.cssText = 'flex:1;min-height:0;position:relative;';

  var locateBtn = document.createElement('div');
  locateBtn.title = '定位到当前位置';
  locateBtn.style.cssText = 'position:absolute;bottom:20px;right:20px;width:40px;height:40px;background:#fff;border:1px solid #E5E7EB;border-radius:4px;display:flex;align-items:center;justify-content:center;cursor:pointer;z-index:10;font-size:18px;';
  locateBtn.innerHTML = '📍';
  mapDiv.appendChild(locateBtn);

  // 底部栏
  var ftr = document.createElement('div');
  ftr.style.cssText = 'padding:10px 18px;border-top:1px solid #E5E7EB;display:flex;justify-content:space-between;align-items:center;flex-shrink:0;';

  var coord = document.createElement('span');
  coord.style.cssText = 'font-size:12px;color:#8E8E8E;';
  coord.textContent = '点击地图选择位置，或点击右下角定位按钮';

  var addBtn = document.createElement('button');
  addBtn.textContent = '添加此位置';
  addBtn.style.cssText = 'padding:6px 22px;border:none;border-radius:4px;background:#3E6AE1;color:#fff;font-weight:500;cursor:pointer;font-size:13px;height:36px;';
  addBtn.onclick = function() {
    var lng = _markerLng, lat = _markerLat;
    if (!lng || !lat) { alert('请先在地图上选择位置'); return; }
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

  // 地图
  var map = new AMap.Map('map-dialog-map', { zoom: 16, center: [116.397428, 39.90923], resizeEnable: true });

  function placeMarker(lng, lat) {
    _markerLng = lng; _markerLat = lat;
    map.clearMap();
    new AMap.Marker({ position: [lng, lat], map: map });
    coord.textContent = '已选: 经度 ' + lng.toFixed(6) + ' , 纬度 ' + lat.toFixed(6);
    coord.style.color = '#3E6AE1';
  }

  map.on('click', function(e) { placeMarker(e.lnglat.getLng(), e.lnglat.getLat()); });

  locateBtn.onclick = function() {
    coord.textContent = '正在获取位置...'; coord.style.color = '#B8860B';
    if (!navigator.geolocation) { coord.textContent = '浏览器不支持定位'; coord.style.color = '#DC2626'; return; }
    navigator.geolocation.getCurrentPosition(
      function(pos) {
        var lng = pos.coords.longitude, lat = pos.coords.latitude;
        map.setCenter([lng, lat]); placeMarker(lng, lat);
        map.setStatus({ dragEnable: false });
        setTimeout(function() { map.setStatus({ dragEnable: true }); }, 3000);
      },
      function(err) { coord.textContent = '无法获取位置，请检查浏览器定位权限'; coord.style.color = '#DC2626'; },
      { enableHighAccuracy: true, timeout: 15000 }
    );
  };
}