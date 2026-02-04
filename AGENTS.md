# AGENTS.md（给 AI Coding 工具）

## 项目概况
- 项目：Calibre-Web（基于 Python/Flask 的电子书管理 Web 应用，使用 Calibre 数据库）。
- 上游仓库：https://github.com/janeczku/calibre-web （本项目为其 fork，心愿单方案见 `calibre-web-wishlist-plan.md`）。
- 主要技术栈：Python（后端）、HTML/Jinja 模板、JavaScript、CSS。
- 数据：Calibre 的 `metadata.db`（SQLite），以及 Calibre-Web 自身的 `app.db`。

## 目录结构（高层）
- `cps/`：应用主体（Flask 应用、路由、服务与工具代码）。
- `cps/static/`：静态资源（JS/CSS/图片/第三方库）。
- `cps/templates/`：Jinja 模板。
- `cps.py`：本地启动入口。
- `library/`：示例 Calibre 库（包含 `metadata.db`）。
- `app.db`：应用运行数据库（本地开发可视为可丢弃）。
- `calibre-web-wishlist-plan.md`：心愿单功能方案与部署说明。

## 本地运行（开发）
1. 创建并激活虚拟环境：
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```
2. 安装依赖：
   ```bash
   pip install -r requirements.txt
   ```
3. 启动服务（二选一）：
   - 直接运行：
     ```bash
     python3 cps.py
     ```
   - 脚本入口：
     ```bash
     cps
     ```
4. 浏览器访问：
   - Web UI：`http://localhost:8083`
   - OPDS：`http://localhost:8083/opds`

## 默认账号（开发）
- 用户名：`admin`
- 密码：`admin123`

## Calibre 数据库配置（开发）
- 需要提供 Calibre 库路径（包含 `metadata.db` 的目录）。
- 本地可用示例库：`library/metadata.db`。
- 在管理后台设置 “Location of Calibre database”。

## 测试说明
- 本仓库不包含主要的自动化测试套件。
- 官方测试在独立仓库：`OzzieIsaacs/calibre-web-test`。
- 前端可用 ESLint（配置见 `.eslintrc`）。

## 心愿单功能相关改动点（参考）
- 导航入口：`cps/templates` 中的基础布局/导航模板。
- 新增页面：`cps/templates/wishlist.html`。
- 新增路由：`GET /wishlist`、`POST /wishlist/submit`（通常在 `cps/` 的主路由模块）。
- 外部 webhook：按 `calibre-web-wishlist-plan.md` 转发到 n8n。

## 约定与注意事项
- `app.db` 为本地状态，开发时可覆盖。
- 不要提交敏感信息。Webhook 地址与凭证应通过环境变量或配置注入。
- 代码风格尽量保持与现有 Flask + Jinja 结构一致。
