#!/bin/bash

echo "=========================================="
echo "  Forum-Bot 诊断工具"
echo "=========================================="

# 进入容器执行诊断
docker exec forum-bot bash -c '
echo "1. 检查 Python 路径..."
echo "PYTHONPATH: $PYTHONPATH"
echo ""

echo "2. 检查目录结构..."
ls -la /app/
echo ""

echo "3. 检查模块文件..."
ls -la /app/backend/
ls -la /app/scheduler/
echo ""

echo "4. 测试模块导入..."
python -c "
import sys
sys.path.insert(0, \"/app\")

try:
    import backend
    print(\"✅ backend 包导入成功\")
except Exception as e:
    print(f\"❌ backend 导入失败: {e}\")

try:
    import scheduler
    print(\"✅ scheduler 包导入成功\")
except Exception as e:
    print(f\"❌ scheduler 导入失败: {e}\")

try:
    from scheduler.scheduler_main import ForumBotScheduler
    print(\"✅ ForumBotScheduler 导入成功\")
except Exception as e:
    print(f\"❌ ForumBotScheduler 导入失败: {e}\")
    import traceback
    traceback.print_exc()
"
echo ""

echo "5. 查看 scheduler 错误日志..."
tail -n 50 /app/logs/scheduler.log
echo ""

echo "6. 查看 supervisor 日志..."
tail -n 50 /app/logs/supervisord.log
'
