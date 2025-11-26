#!/bin/bash
set -e

echo "=========================================="
echo "  Forum-Bot 启动中..."
echo "=========================================="

# 设置 Python 路径
export PYTHONPATH=/app:$PYTHONPATH

# 检查并创建必要的目录
mkdir -p /app/data /app/logs

# 初始化数据库（如果不存在）
if [ ! -f /app/data/forum_bot.db ]; then
    echo "初始化数据库..."
    cd /app
    python -c "
import sys
sys.path.insert(0, '/app')
from backend.database.db import init_db
init_db('/app/data/forum_bot.db')
print('数据库初始化完成')
" || {
        echo "❌ 数据库初始化失败"
        exit 1
    }
fi

# 验证模块导入
echo "验证模块导入..."
python -c "
import sys
sys.path.insert(0, '/app')

# 测试导入
try:
    from backend.database.db import init_db, get_db
    print('✅ backend.database 模块导入成功')
    
    from backend.models import User, Site, TaskLog, NotificationConfig
    print('✅ backend.models 模块导入成功')
    
    from backend.services import SiteService, TaskService
    print('✅ backend.services 模块导入成功')
    
    from scheduler.task_runner import TaskRunner
    print('✅ scheduler.task_runner 模块导入成功')
    
    from scheduler.scheduler_main import ForumBotScheduler
    print('✅ scheduler.scheduler_main 模块导入成功')
    
    print('✅ 所有模块导入验证成功')
except Exception as e:
    print(f'❌ 模块导入失败: {e}')
    import traceback
    traceback.print_exc()
    sys.exit(1)
" || {
    echo "❌ 模块验证失败"
    exit 1
}

echo "=========================================="
echo "  启动所有服务..."
echo "=========================================="
echo "  - Nginx (端口 80)"
echo "  - Backend API (内部端口 5000)"
echo "  - Scheduler (后台任务)"
echo "=========================================="

# 启动 Supervisor
exec /usr/bin/supervisord -c /etc/supervisor/conf.d/supervisord.conf
