FROM --platform=linux/amd64 python:3.9-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive \
    PYTHONPATH=/app

# ==================== 安装基础依赖 ====================
RUN apt-get update && apt-get install -y \
    wget \
    curl \
    gnupg \
    ca-certificates \
    supervisor \
    nginx \
    sqlite3 \
    && rm -rf /var/lib/apt/lists/*

# ==================== 添加 Chrome 源 ====================
RUN wget -q -O /tmp/google-chrome.gpg https://dl.google.com/linux/linux_signing_key.pub \
    && gpg --dearmor -o /usr/share/keyrings/google-chrome-keyring.gpg /tmp/google-chrome.gpg \
    && echo "deb [arch=amd64 signed-by=/usr/share/keyrings/google-chrome-keyring.gpg] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list \
    && rm /tmp/google-chrome.gpg

# ==================== 安装 Chrome ====================
RUN apt-get update && apt-get install -y \
    google-chrome-stable \
    && rm -rf /var/lib/apt/lists/*

# ==================== 验证安装 ====================
RUN google-chrome --version

# ==================== 安装 Python 依赖 ====================
COPY backend/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt && rm /tmp/requirements.txt

# ==================== 复制项目文件 ====================
COPY . .

# ==================== 创建必要目录 ====================
RUN mkdir -p /app/data /app/logs

# ==================== ⭐ 构建前端（新增）====================
# 如果您已经有构建好的 dist 目录，跳过这一步
# 如果需要在 Docker 中构建前端，取消下面的注释：

# FROM node:18-alpine AS frontend-builder
# WORKDIR /app/frontend
# COPY frontend/package*.json ./
# RUN npm install
# COPY frontend/ ./
# RUN npm run build

# 然后在主 FROM 后添加：
# COPY --from=frontend-builder /app/frontend/dist /app/frontend/dist

# ==================== ⭐ 复制预构建的前端（如果已有）====================
# 如果您的仓库中已经有 frontend/dist 目录：
# COPY frontend/dist /app/frontend/dist

# ==================== 临时方案：创建简单的 index.html ====================
RUN mkdir -p /app/frontend/dist && \
    echo '<!DOCTYPE html><html><head><meta charset="UTF-8"><title>Forum-Bot</title></head><body><h1>Forum-Bot 正在运行</h1><p>前端正在部署中...</p><p>API 端点：<a href="/api/health">/api/health</a></p></body></html>' > /app/frontend/dist/index.html

# ==================== 复制配置文件 ====================
COPY deploy/nginx.conf /etc/nginx/sites-available/default
COPY deploy/supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# ==================== 设置权限 ====================
RUN chmod +x /app/deploy/entrypoint.sh

# ==================== 暴露端口 ====================
EXPOSE 80

# ==================== 健康检查 ====================
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost/api/health || exit 1

# ==================== 启动入口 ====================
ENTRYPOINT ["/app/deploy/entrypoint.sh"]
