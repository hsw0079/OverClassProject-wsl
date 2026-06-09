# Git 回滚演练复盘

## 操作序列与后果

| # | 操作 | 结果 | 状态 |
|---|------|------|------|
| 1 | `git clean -fdx --dry-run` | 预览会删什么 | ✅ |
| 2 | `git clean -fdx` | **删掉了 `.venv`** | ❌ 虚拟环境丢失 |
| 3 | `git checkout 31c269a` | 切到 simpleui 老版本 | ✅ |
| 4 | — | PyCharm 检测 SDK 路径失效，自动切到系统 Python | ⚠️ |
| 5 | `git checkout main` | 回到最新版 | ✅ |
| 6 | `python manage.py runserver` | `.venv` 为空，Django 未安装 | ❌ `ModuleNotFoundError` |
| 7 | `pip install ...` | 重装所有依赖 | ✅ |
| 8 | `git pull` (PyCharm 自动) | 本地/远程分叉，触发 merge | ❌ 4 个文件冲突 |
| 9 | `git merge --abort` | 中止 merge | ✅ |
| 10 | `git checkout 31c269a` | 被 pycache 和 git回滚.txt 阻止 | ❌ |
| 11 | `git checkout -- pycache` + `git stash` | 丢弃 pycache，暂存笔记 | ✅ |
| 12 | `git checkout 31c269a` | `esbuild.exe` 被 Vite 占用 | ❌ |
| 13 | `Ctrl+C` 停 Vite + `git checkout 31c269a` | 切成功 | ✅ |
| 14 | `git checkout main` | `esbuild.exe` 仍挡住（旧 commit 残留） | ❌ |
| 15 | `rmdir /s /q node_modules` + `git checkout main` | 切回 main | ✅ |
| 16 | `git stash pop` | 笔记恢复 | ✅ |
| 17 | `npm install` | 重装前端依赖 | ✅ |

---

## 三大根因

| # | 原因 | 后果 |
|---|------|------|
| 没有 `.gitignore` | `git clean -fdx` 删了 `.venv` | 依赖全丢 |
| 老 commit 里 `node_modules` 被 git 追踪 | 切回来时与已 gitignore 的 `node_modules` 冲突 | esbuild.exe 反复挡路 |
| PyCharm 默认 `Merge` 模式自动同步 | `git pull` 触发分叉合并 | 4 个文件冲突 |

---

## 已加的防线

| 防线 | 说明 |
|------|------|
| `.gitignore` | 保护 `.venv`、`node_modules`、`__pycache__`、`.idea` |
| `requirements.txt` | venv 丢了可一键恢复：`pip install -r requirements.txt` |
| PyCharm 更新方式 | `Merge` → `Rebase`，关闭自动 fetch |

---

## 安全回滚速查

```
git stash              # 暂存当前工作（代替 git clean）
git checkout <hash>    # 切到目标版本
git checkout main      # 回来
git stash pop          # 恢复工作
```

**被 pycache 挡：**

```
git checkout -- .
git checkout <hash>
```

**被 node_modules 挡：**

```
rmdir /s /q frontend\node_modules
git checkout main
npm install
```
