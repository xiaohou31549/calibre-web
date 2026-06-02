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
3. 配置本地环境变量（推荐用 `.env` 放在项目根目录，勿提交）：
   ```bash
   FEISHU_APP_ID="..."
   FEISHU_APP_SECRET="..."
   FEISHU_BITABLE_APP_TOKEN="..."
   FEISHU_BITABLE_TABLE_ID="..."
   ```
4. 启动服务（二选一）：
   - 直接运行：
     ```bash
     python3 cps.py
     ```
   - 脚本入口：
     ```bash
     cps
     ```
   - 如果使用 `.env`，建议用脚本启动：
     ```bash
     ./scripts/dev_run.sh
     ```
5. 浏览器访问：
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

## 心愿单功能（用户侧：提交心愿单）
- 导航入口：`cps/templates/layout.html` 中的导航菜单（红色 ❤️「书籍心愿单」）。
- 页面：`cps/templates/wishlist.html`。
- 路由：`GET /wishlist`、`POST /wishlist/submit`（`cps/web.py`）。
- 数据存储：后端**直写**飞书多维表格（`cps/services/feishu.py` 的 `create_wishlist_record`）。
  注意：早期方案文档写的是“后端转发 n8n Webhook → n8n 写飞书”，实际实现已改为后端直连飞书 API。

## 心愿单管理（管理员侧：上架并通知用户）
- 导航入口：`cps/templates/layout.html`，仅 `current_user.role_admin()` 可见的「心愿单管理」。
- 页面：`cps/templates/admin_wishlist.html`。
- 路由（`cps/admin.py`，均带 `@admin_required`）：
  - `GET /admin/wishlist`：从飞书读取全部心愿单记录并渲染列表。
  - `POST /admin/wishlist/fulfill`：上传电子书 → 建书 → 生成下载链接 → 邮件通知用户 → 回写飞书状态。
- 关键依赖与复用：
  - 上传建书：`cps/editbooks.py` 的 `create_book_from_uploaded_file()`（复用上传流程，返回 book_id）。
  - 发邮件：`cps/tasks/mail.py` 的 `TaskEmail`（已支持可选 `html=` 参数发送 HTML 正文）。
  - 飞书读写：`cps/services/feishu.py` 的 `list_wishlist_records()` 与 `update_wishlist_record()`。
- 前置条件：
  - 飞书多维表需有「状态」单选字段（选项含「已通知」），字段/选项名常量在 `cps/admin.py` 顶部（`WISHLIST_FIELD_*` / `WISHLIST_STATUS_DONE`），与表列名不一致时改这里。
  - 站点需配置 SMTP（否则 `fulfill` 会在上传前拦截并提示）。
  - 用户收到的下载链接指向 `web.show_book` 书籍页，需站点开启匿名浏览/匿名下载，游客才能访问。

## 部署
- CI：`.github/workflows/docker-publish.yml`，push 到 `master` 触发：构建镜像推 GHCR → SSH 到 VPS `docker compose pull/up -d` → 飞书 Webhook 通知部署结果。
- 镜像：`Dockerfile` 基于 `lscr.io/linuxserver/calibre-web:latest` 叠加本仓库代码。
- 生产 SMTP 用 Gmail（smtp.gmail.com:465 SSL + 应用专用密码），在管理后台「编辑邮件服务器设置」配置，不需要改代码。

## 本地开发注意
- 上传电子书依赖 `libmagic`（MIME 校验）。macOS 若未安装会导致所有上传被拒，需 `brew install libmagic`；
  或临时在本地 `app.db` 设 `config_check_extensions=0` 绕过（仅本地调试用）。线上镜像自带 libmagic。

## 约定与注意事项
- `app.db` 为本地状态，开发时可覆盖。
- 不要提交敏感信息。Webhook 地址与凭证应通过环境变量或配置注入。
- 代码风格尽量保持与现有 Flask + Jinja 结构一致。
