这是一个完善的 `README.md` 文档，基于你提供的项目代码和结构编写。它涵盖了项目介绍、功能特性、部署指南、配置说明以及开发指南。

***

# Forum-Bot - 通用论坛自动化机器人平台

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.9+-blue.svg" alt="Python">
  <img src="https://img.shields.io/badge/Vue-3.x-green.svg" alt="Vue">
  <img src="https://img.shields.io/badge/Docker-Ready-blue.svg" alt="Docker">
  <img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License">
</p>

**Forum-Bot** 是一个功能强大的通用论坛自动化机器人平台。它结合了现代化的 Web 管理界面、Selenium 自动化技术和 AI 大模型能力，能够实现论坛的自动签到、智能回复、活跃回帖等功能。

本项目采用前后端分离架构，支持 Docker 一键部署，并内置了多种主流论坛架构（Flarum, Discourse 等）的适配模板。

## ✨ 核心特性

*   **🌐 多站点管理**：支持同时管理无限个论坛站点，独立配置任务策略。
*   **🧩 预设模板库**：内置 DeepFlood, NodeLoc, LinuxDo 等常见论坛配置，支持 Flarum 和 Discourse 架构的一键导入。
*   **🤖 AI 智能驱动**：
    *   集成 OpenAI 兼容接口（支持 GPT-3.5/4, Claude, 通义千问等）。
    *   智能内容分析：自动识别帖子主题，过滤广告和垃圾内容。
    *   自然语言回复：根据帖子内容生成上下文相关的回复，拒绝"万能回复"。
*   **🔐 灵活认证**：
    *   **Cookie 登录**（推荐）：通过 Cookie 字符串直接登录，绕过复杂验证码。
    *   **账号密码登录**：支持传统的自动化表单登录。
*   **📅 精准调度**：基于 Cron 表达式的任务调度，支持随机延迟，模拟真实用户行为。
*   **🔔 全渠道通知**：任务执行结果实时推送，支持：
    *   Telegram Bot
    *   企业微信
    *   钉钉
    *   飞书
    *   PushPlus
    *   Bark (iOS)
    *   Gotify
    *   SMTP 邮件
*   **🛡️ 浏览器伪装**：使用 `undetected-chromedriver` 和指纹伪装技术，降低被检测风险。

## 📸 界面预览

*(此处可添加仪表板、站点管理、任务日志的截图)*

## 🚀 快速部署 (Docker)

推荐使用 Docker Compose 进行一键部署（All-in-One 镜像）。

### 1. 准备目录和文件

创建项目目录并下载 `docker-compose.yml`：

```bash
mkdir forum-bot && cd forum-bot
# 创建数据和日志目录
mkdir -p data logs
```

创建 `docker-compose.yml` 文件：

```yaml
version: '3.8'

services:
  forum-bot:
    image: ghcr.io/yunxzh/forum-bot:aio
    container_name: forum-bot
    restart: unless-stopped
    ports:
      - "80:80"  # Web 访问端口
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
    environment:
      - SECRET_KEY=change_this_random_string
      - JWT_SECRET_KEY=change_this_jwt_secret
      # 浏览器配置
      - HEADLESS=true
      - IN_DOCKER=true
      # 时区
      - TZ=Asia/Shanghai
```

### 2. 启动服务

```bash
docker-compose up -d
```

### 3. 访问管理后台

启动成功后，浏览器访问：`http://localhost` (或服务器 IP)。

*   **默认账号**：`admin`
*   **默认密码**：`admin123`

> ⚠️ **注意**：首次登录后请务必在右上角个人中心修改密码！

## ⚙️ 配置说明

### AI 配置 (必需)
为了使用自动回复功能，你需要在后台「全局配置 -> AI 配置」中设置：
*   **提供商**：如 `openai`, `new-api`。
*   **API 地址**：OpenAI 官方或中转 API 地址。
*   **API 密钥**：`sk-xxxx`。
*   **模型名称**：如 `gpt-3.5-turbo`, `qwen-turbo` 等。

### 添加站点
在「站点管理」中点击“新增站点”：
1.  **快速模板**：如果站点是知名论坛（如 LinuxDo, NodeLoc），可直接选择预设模板。
2.  **Cookie 获取**：在浏览器中按 F12 打开开发者工具，在网络请求或 Application 面板中复制完整的 Cookie 字符串。
3.  **Cron 表达式**：设置执行时间，例如 `0 9 * * *` 表示每天上午 9 点执行。

## 🛠️ 本地开发

如果你想参与开发或修改源码：

### 环境要求
*   Python 3.9+
*   Node.js 18+
*   Chrome 浏览器

### 后端运行

```bash
cd backend
# 安装依赖
pip install -r requirements.txt
# 设置环境变量
export PYTHONPATH=$PYTHONPATH:.
# 初始化数据库
python database/init_db.py
# 运行服务
python app.py
```

### 前端运行

```bash
cd frontend
# 安装依赖
npm install
# 开发模式
npm run dev
```

### 调度器运行

```bash
# 在项目根目录下
python -m scheduler.scheduler_main
```

## 📂 项目结构

```text
forum-bot/
├── backend/            # Python Flask 后端 API
│   ├── api/            # API 路由
│   ├── database/       # 数据库操作
│   ├── models/         # 数据模型
│   └── services/       # 业务逻辑
├── frontend/           # Vue 3 前端源码
├── core/               # 核心自动化引擎
│   ├── ai/             # AI 回复生成与分析
│   ├── browser/        # 浏览器与 Cookie 管理
│   ├── executors/      # 任务执行器 (签到/回复)
│   └── parsers/        # 页面解析器
├── scheduler/          # APScheduler 任务调度
├── presets/            # 论坛预设配置 JSON
├── deploy/             # 部署脚本与配置
└── Dockerfile          # All-in-One 构建文件
```

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！
1.  Fork 本仓库
2.  新建 Feat_xxx 分支
3.  提交代码
4.  新建 Pull Request

## ⚠️ 免责声明

*   本项目仅供学习和研究使用。
*   使用本项目产生的任何后果（如账号被封禁）由使用者自行承担。
*   请勿将本项目用于发布垃圾广告、恶意灌水等违反法律法规或论坛规定的用途。

## 📄 License

[MIT License](LICENSE)
