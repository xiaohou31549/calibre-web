# Calibre-Web 心愿单功能方案（二：集成页面 + 外部存储）

## 目标
在现有 `calibre-web` 页面中增加一个“心愿单”入口，用户可匿名提交想看的电子书（书名、作者、邮箱、备注）。提交后写入飞书“多维表格”。你后续可手动或自动化下载电子书并导入 `calibre-web`。

## 方案（二）技术方案
基于开源 `calibre-web` **fork 新仓库进行修改**：在 `calibre-web` 内增加页面和按钮，数据存外部（飞书多维表）。用户在 `calibre-web` 内提交心愿单，后端把数据转发给 `n8n` Webhook，`n8n` 写入飞书多维表。此方案兼顾用户体验与可维护性。

开源的 calibre-web 仓库地址：https://github.com/janeczku/calibre-web

**优点**
- 用户体验简单：入口在 `calibre-web` 导航内
- 可维护性好：不污染 `calibre-web` 数据库
- 便于自动化：通过 `n8n` 扩展下载、导入流程

## 功能需求（确认版）
- 心愿单：全站一个列表（非用户个人列表）。
- 提交方式：匿名用户可提交。
- 表单字段：书名（必填）、作者、邮箱、备注。
- 存储：飞书多维表格。

## 架构概览
1. `calibre-web` 前端：导航增加“心愿单”入口 → `/wishlist` 页面表单
2. `calibre-web` 后端：新增路由 `/wishlist` 和 `/wishlist/submit`
3. `n8n`：Webhook 接收 POST → 写入飞书多维表
4. 飞书多维表：保存心愿单记录

## 多维表字段设计（建议）
- 书名（必填，文本）
- 作者（文本）
- 邮箱（文本）
- 备注（多行文本）
- 提交时间（时间，自动生成）

## calibre-web 改动点（实现参考）
> 具体文件路径以你 fork 的仓库为准，这里只给出方向和功能点。

1. 导航菜单添加“心愿单”入口
   - 修改模板中的导航菜单（常见是 `base.html` 或类似 layout 模板）

2. 新增页面模板
   - 新建 `wishlist.html`（表单 + 提交结果提示）

3. 新增后端路由
   - `GET /wishlist`：渲染表单页面
   - `POST /wishlist/submit`：校验表单 → 转发到 n8n Webhook → 返回成功/失败提示

4. 表单字段校验
   - 书名：必填
   - 作者/邮箱/备注：可选
   - 邮箱格式：可做轻量校验（可选）

## n8n 流程设计（建议）
1. Webhook 节点（POST）
   - 接收 JSON：`title, author, email, note`
2. Set 节点
   - 映射字段到飞书表结构
   - 增加 `submitted_at`（当前时间）
3. 飞书多维表节点
   - 插入一条记录

## 飞书个人版注意事项
- 个人版可以创建多维表，但 API 写入需要应用凭证。
- 如果暂时没有飞书 App 凭证：
  - 可先用 n8n 内部记录或临时数据库打样
  - 或在飞书开发者后台创建应用后再接通

## 部署与发布（镜像方式，改动最小）
建议把 fork 后的 `calibre-web` 构建为自定义镜像并替换现有部署镜像，这是改动最小、回滚最简单的方式。

**推荐流程**
1. Fork `calibre-web` 并完成代码修改
2. 使用 GitHub Actions 构建镜像并推送到 GHCR（公开仓库可零成本）
3. VPS 上修改 `docker-compose.yml` 中的 `calibre-web` 镜像地址为你的镜像
4. 执行更新：`docker compose pull && docker compose up -d`

**回滚方式**
- 把 `docker-compose.yml` 的镜像改回原镜像（例如 `lscr.io/linuxserver/calibre-web:latest`）
- 重新 `pull` 与 `up -d`

**可选：自动部署**
- GitHub Actions 在构建完成后通过 SSH 触发 VPS 执行 `docker compose pull && up -d`

## 后续自动化（可选）
- 在 n8n 中做定时任务，扫描心愿单记录
- 结合下载工具/脚本自动获取电子书
- 下载完成后自动导入 `calibre-web` 的 books 目录

## 下一步清单（实现前准备）
1. 创建飞书多维表，按字段设计建立列
2. 在 n8n 创建 Webhook 流程，测试写入多维表
3. fork `calibre-web` 仓库，准备自定义镜像构建流程
4. 在 `calibre-web` 中增加页面与路由

---

如需我继续提供：
- `n8n` 详细节点配置和字段映射
- `calibre-web` 具体文件修改位置和代码骨架
- Docker 构建与部署流程
随时告诉我。
