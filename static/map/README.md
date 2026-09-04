# 高德地图配置

请到 https://console.amap.com/dev/ 注册高德开放平台账号，创建应用获取：

1. **Key**（JS API 密钥）
2. **安全密钥**（JS API 安全密钥）

然后在以下文件中替换：
- `frontend/src/views/NavigationDetail.vue` 中的 `AMAP_KEY` 和 `AMAP_SECRET`（SPA 导航）
- `templates/admin/campus_nav/change_list.html` 中 `<script src="...maps?v=2.0&key=...">` 的高德 Key（Admin 地点选择器）

## 校园地图图片

将校园实际地图 JPG 放置于 `static/map/campus_map.jpg`，替换当前占位文件。