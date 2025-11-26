FROM python:3.9-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive \
    PYTHONPATH=/app

# 安装基础工具
RUN apt-get update && apt-get install -y \
    wget \
    curl \
    gnupg \
    supervisor \
    nginx \
    sqlite3 \
    && rm -rf /var/lib/apt/lists/*

# 添加 Chrome 源并安装
RUN wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    && rm -rf /var/lib/apt/lists/*

# 验证 Chrome
RUN google-chrome --version

# 安装 Python 依赖
COPY backend/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# 复制项目
COPY . .

# 创建目录
RUN mkdir -p /app/data /app/logs /app/frontend/dist

# 配置文件
COPY deploy/nginx.conf /etc/nginx/sites-available/default
COPY deploy/supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# 权限
RUN chmod +x /app/deploy/entrypoint.sh

EXPOSE 80

HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost/api/health || exit 1

ENTRYPOINT ["/app/deploy/entrypoint.sh"]
