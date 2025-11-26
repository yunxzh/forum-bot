# 基础镜像
FROM python:3.9-slim

# 设置工作目录
WORKDIR /app

# 设置环境变量
ENV PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive \
    PYTHONPATH=/app

# ==================== 安装基础工具 ====================
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget \
    curl \
    gnupg2 \
    ca-certificates \
    apt-transport-https \
    && rm -rf /var/lib/apt/lists/*

# ==================== 添加 Google Chrome 源并安装 ====================
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | gpg --dearmor -o /usr/share/keyrings/google-chrome.gpg \
    && echo "deb [arch=amd64 signed-by=/usr/share/keyrings/google-chrome.gpg] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list

# ==================== 安装所有依赖 ====================
RUN apt-get update && apt-get install -y --no-install-recommends \
    google-chrome-stable \
    supervisor \
    nginx \
    sqlite3 \
    unzip \
    fonts-liberation \
    libasound2 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libatspi2.0-0 \
    libcups2 \
    libdbus-1-3 \
    libdrm2 \
    libgbm1 \
    libgtk-3-0 \
    libnspr4 \
    libnss3 \
    libwayland-client0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxkbcommon0 \
    libxrandr2 \
    xdg-utils \
    libu2f-udev \
    libvulkan1 \
    && rm -rf /var/lib/apt/lists/*

# ==================== 验证 Chrome 安装 ====================
RUN google-chrome --version && echo "✅ Chrome 安装成功"

# ==================== 安装 Python 依赖 ====================
COPY backend/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt && rm /tmp/requirements.txt

# ==================== 复制项目文件 ====================
COPY . .

# ==================== 创建必要的目录 ====================
RUN mkdir -p /app/data /app/logs /app/frontend/dist

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

# ==================== 启动脚本 ====================
ENTRYPOINT ["/app/deploy/entrypoint.sh"]
