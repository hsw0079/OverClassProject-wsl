# OverClassProject

校园车辆管理系统：车辆进出记录、访客预约、二维码通行、校园导航。后端 Django 6 + DRF，前端 Vue 3 + Vite SPA。

## 项目结构

```
├── OverClassProject/      # Django 配置（URL、settings）
├── apps/
│   ├── vehicle_mgmt/      # 车辆记录、进出记录、访客预约、二维码 API
│   └── campus_nav/        # 校园地点 API（挂载在 /api/admin/locations/）
├── frontend/              # Vue 3 + Vite SPA
├── static/                # 静态资源（含校园地图 static/map/campus_map.jpg）
├── templates/             # Django 模板
└── manage.py
```

## 环境要求

- Python 3.x，MySQL 5.7+（本地库 `overclassproject`，`localhost:3306`）
- Node.js + npm

## 后端启动

```text
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_data        # 可选：创建示例数据
python manage.py runserver 8001   # Vite 代理默认指向 8001
```

注意：`requirements.txt` 未列出 `djangorestframework`、`django-cors-headers`、`qrcode`，需额外安装。

## 前端启动

```text
cd frontend
npm ci
npm run dev    # 监听 5173，/api、/media、/static 代理到 127.0.0.1:8001
```

生产构建：`npm run build`

## 主要 API

| 接口 | 说明 |
| --- | --- |
| `/api/auth/register/` | 注册（Token 认证） |
| `/api/auth/login/` | 登录 |
| `/api/auth/user/` | 当前用户信息 |
| `/api/appointments/` | 预约 CRUD（需认证） |
| `/api/appointments/<id>/qr/` | 预约二维码 |
| `/api/appointments/<id>/qr-info/` | 二维码票据信息 |
| `/api/admin/locations/` | 校园地点（公开读取） |

## 常用命令

```text
python manage.py check
python manage.py test
python manage.py makemigrations && python manage.py migrate
python manage.py purge_external_vehicles   # 删除所有 ExternalVehicle
python manage.py collectstatic
```

## 注意事项

- 配置为开发用途（`DEBUG`、通配 hosts/CORS、硬编码凭据），不要当作生产配置。
- 前端通过 `localStorage` 保存 token，请求头 `Authorization: Token <token>`。
- `seed_data` 每次运行都会新建进出记录，重复运行前注意数据清理。