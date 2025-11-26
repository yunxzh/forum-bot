#!/bin/bash
set -e

echo "=========================================="
echo "  Forum-Bot 启动中..."
echo "=========================================="

# 检查并创建必要的目录
mkdir -p /app/data /app/logs

# 初始化数据库（如果不存在）
if [ ! -f /app/data/forum_bot.db ]; then
    echo "初始化数据库..."
    cd /app && python -c "
from backend.database.db import init_db
init_db('/app/data/forum_bot.db')
print('数据库初始化完成')
"
fi

echo "=========================================="
echo "  启动所有服务..."
echo "=========================================="
echo "  - Nginx (端口 80)"
echo "  - Backend API (内部端口 5000)"
echo "  - Scheduler (后台任务)"
echo "=========================================="

# 启动 Supervisor
exec /usr/bin/supervisord -c /etc/supervisor/conf.d/supervisord.conf
