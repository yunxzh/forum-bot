# 基础镜像
FROM python:3.9-slim

# 设置工作目录
WORKDIR /app

# 设置环境变量
ENV PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive \
    DISPLAY=:99 \
    PYTHONPATH=/app

# ==================== 安装系统依赖和 Chrome ====================
RUN apt-get update && apt-get install -y \
    # 基础工具
    wget \
    curl \
    gnupg \
    unzip \
    supervisor \
    nginx \
    sqlite3 \
    # Chrome 依赖包
    fonts-liberation \
    libappindicator3-1 \
    libasound2 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libcups2 \
    libdbus-1-3 \
    libgdk-pixbuf2.0-0 \
    libnspr4 \
    libnss3 \
    libx11-xcb1 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    xdg-utils \
    libgbm1 \
    libxss1 \
    libxtst6 \
    ca-certificates \
    # 中文字体
    fonts-wqy-zenhei \
    fonts-wqy-microhei \
    && rm -rf /var/lib/apt/lists/*

# ==================== 安装 Google Chrome ====================
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    && rm -rf /var/lib/apt/lists/*

# ==================== 验证 Chrome 安装 ====================
RUN google-chrome --version && echo "✅ Chrome 安装成功"

# ==================== 复制并安装 Python 依赖 ====================
# ⭐ 修复：使用正确的路径
COPY backend/requirements.txt /app/backend/requirements.txt
RUN pip install --no-cache-dir -r /app/backend/requirements.txt

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
