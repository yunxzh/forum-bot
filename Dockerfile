# ============================================
# 阶段 1: 前端构建
# ============================================
FROM node:18-alpine AS frontend-builder

WORKDIR /app/frontend

COPY frontend/package*.json ./
RUN npm install

COPY frontend/ ./
RUN npm run build

# ============================================
# 阶段 2: 最终镜像
# ============================================
FROM python:3.9-slim

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    chromium \
    chromium-driver \
    curl \
    nginx \
    supervisor \
    --no-install-recommends && \
    rm -rf /var/lib/apt/lists/*

# 设置环境变量
ENV DRIVER_EXECUTABLE_PATH=/usr/bin/chromedriver
ENV IN_DOCKER=true
ENV TZ=Asia/Shanghai
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# 设置时区
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# 自动检测Chrome版本
RUN CHROME_MAJOR_VERSION=$(chromium --version | grep -oP 'Chromium \K\d+') && \
    export CHROME_VERSION=${CHROME_MAJOR_VERSION}

# 设置工作目录
WORKDIR /app

# 复制并安装 Python 依赖
COPY backend/requirements.txt ./backend/
RUN pip install --no-cache-dir -r backend/requirements.txt

# 复制项目文件 - 注意顺序和结构
COPY backend/ ./backend/
COPY core/ ./core/
COPY scheduler/ ./scheduler/
COPY presets/ ./presets/

# 创建 __init__.py 文件确保模块可导入
RUN touch /app/__init__.py && \
    touch /app/backend/__init__.py && \
    touch /app/core/__init__.py && \
    touch /app/scheduler/__init__.py

# 从构建阶段复制前端构建产物
COPY --from=frontend-builder /app/frontend/dist /usr/share/nginx/html

# 复制配置文件
COPY deploy/nginx.conf /etc/nginx/sites-available/default
COPY deploy/supervisord.conf /etc/supervisor/conf.d/supervisord.conf
COPY deploy/entrypoint.sh /entrypoint.sh

RUN chmod +x /entrypoint.sh

# 创建必要的目录
RUN mkdir -p /app/data /app/logs /var/log/supervisor

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:80/api/health || exit 1

# 暴露端口
EXPOSE 80

# 启动入口
ENTRYPOINT ["/entrypoint.sh"]
