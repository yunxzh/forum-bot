# ==================== 第一阶段：构建前端 ====================
FROM node:18-alpine AS frontend-builder

WORKDIR /app/frontend

# 复制依赖文件并安装
COPY frontend/package*.json ./
# 使用 npm ci 安装更稳定，或者用 install
RUN npm install

# 复制源代码并构建
COPY frontend/ ./
RUN npm run build


# ==================== 第二阶段：构建运行环境 ====================
FROM --platform=linux/amd64 python:3.9-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive \
    PYTHONPATH=/app \
    TZ=Asia/Shanghai

# ==================== 安装基础依赖 (含时区数据) ====================
RUN apt-get update && apt-get install -y \
    wget \
    curl \
    gnupg \
    ca-certificates \
    supervisor \
    nginx \
    sqlite3 \
    tzdata \
    && ln -fs /usr/share/zoneinfo/Asia/Shanghai /etc/localtime \
    && dpkg-reconfigure -f noninteractive tzdata \
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

# ==================== 复制项目后端文件 ====================
COPY . .

# ==================== 创建必要目录 ====================
RUN mkdir -p /app/data /app/logs /app/frontend/dist

# ==================== 复制构建好的前端文件 ====================
COPY --from=frontend-builder /app/frontend/dist /app/frontend/dist

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
