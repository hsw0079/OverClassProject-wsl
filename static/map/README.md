# 高德地图配置

请到 https://console.amap.com/dev/ 注册高德开放平台账号，创建应用获取：

1. **Key**（JS API 密钥）
2. **安全密钥**（JS API 安全密钥）

然后在以下文件中替换：
- `frontend/src/views/NavigationDetail.vue` 中的 `AMAP_KEY` 和 `AMAP_SECRET`
- `static/admin/js/campus_map_admin.js` 中的高德 Key（通过 Admin Media 引入时配置）

## 校园地图图片

将校园实际地图 JPG 放置于 `static/map/campus_map.jpg`，替换当前占位文件。