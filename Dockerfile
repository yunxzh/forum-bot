# ============================================
# 阶段 1: 前端构建
# ============================================
FROM node:18-alpine AS frontend-builder

WORKDIR /app/frontend

# 复制前端依赖文件
COPY frontend/package*.json ./

# 安装依赖
RUN npm install

# 复制前端源码
COPY frontend/ ./

# 构建前端
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

# 复制项目文件
COPY backend/ ./backend/
COPY core/ ./core/
COPY scheduler/ ./scheduler/
COPY presets/ ./presets/

# 从构建阶段复制前端构建产物
COPY --from=frontend-builder /app/frontend/dist /usr/share/nginx/html

# 复制 Nginx 配置
COPY deploy/nginx.conf /etc/nginx/sites-available/default

# 复制 Supervisor 配置
COPY deploy/supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# 复制启动脚本
COPY deploy/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# 创建必要的目录
RUN mkdir -p /app/data /app/logs /var/log/supervisor

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:80/api/health || exit 1

# 暴露端口（只需要一个端口）
EXPOSE 80

# 启动入口
ENTRYPOINT ["/entrypoint.sh"]
