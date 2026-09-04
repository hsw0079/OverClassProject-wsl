# Agent 指南

## 项目结构

- 这是一个双进程应用：Django 后端在仓库根目录，Vue 3/Vite SPA 在 `frontend/`。
- 后端 URL 配置在 `OverClassProject/urls.py`；主要业务 app 是 `apps.vehicle_mgmt`（车辆记录、admin、预约、二维码 API）和 `apps.campus_nav`（校园地点 API）。注意 `apps.campus_nav` 的路由挂载在 `api/admin/` 下，所以地点接口位于 `/api/admin/locations/`，而不是 `/api/locations/`。
- `EntryExitRecord.save()` 会去除车牌号首尾空白、将已登记车牌关联到 `SchoolVehicle`，否则创建/关联 `ExternalVehicle`；需与 `apps/vehicle_mgmt/admin.py` 中的重复逻辑保持一致。
- 前端使用 `localStorage` 中的 token 认证，通过 `frontend/src/api/index.js` 发送 `Authorization: Token <token>`；预约相关 API 需要认证，校园地点的读取是公开的。

## 环境

- `OverClassProject/settings.py` 使用本地 MySQL 数据库 `overclassproject`（`localhost:3306`）；执行迁移或测试前必须保证 MySQL 和可用数据库账号就绪。
- 配置均为开发用途且硬编码（`DEBUG`、通配 hosts/CORS、secret 和数据库凭据）；不要将其当作生产配置，也不要往源码里再加密钥。
- 按 `requirements.txt` 安装依赖，但注意当前代码导入还需要 `djangorestframework`、`django-cors-headers` 和 `qrcode`，它们并未列在其中。`requirements.txt` 还锁定了应用本身不用的打包/构建工具（frida、Nuitka、PyInstaller）。
- 前端有自己的 lockfile；在 `frontend/` 下用 `npm ci` 安装依赖。

## 命令

后端命令在仓库根目录运行：

```text
python manage.py migrate
python manage.py check
python manage.py test
python manage.py test apps.vehicle_mgmt.tests.AdminPageTests.test_stats_dashboard
python manage.py runserver 8001
```

前端命令在 `frontend/` 下运行：

```text
npm run dev
npm run build
```

- Vite 监听 `5173` 端口，并把 `/api`、`/media`、`/static` 代理到 `127.0.0.1:8001`；调试 SPA 时用 `runserver 8001`，而不是 Django 默认端口。
- 前端没有配置 lint、typecheck 或 test 脚本；前端验证用 `npm run build`，后端验证用 Django `check`/`test`。
- 修改模型后先运行 `python manage.py makemigrations` 再 `python manage.py migrate`；生成的迁移文件放在对应 app 的 `migrations/` 目录下。

## 数据与资源

- `python manage.py seed_data` 会创建示例数据；车辆和预约种子用 `get_or_create`，但进出记录每次运行都会新建，所以在需要保持数据干净的场合不要重复运行。
- `python manage.py purge_external_vehicles` 和对应的 Admin 操作会删除所有 `ExternalVehicle` 记录；相关的进出记录外键使用 `SET_NULL`，进出记录本身会保留。
- 源静态资源放在 `static/`；`STATIC_ROOT` 是 `staticfiles/`，由 `python manage.py collectstatic` 更新。
- 校园导航把高德地图凭据作为常量写在 `frontend/src/views/NavigationDetail.vue`；地图配置及 `static/map/campus_map.jpg` 资源说明见 `static/map/README.md`。
