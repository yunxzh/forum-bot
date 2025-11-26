"""
数据库初始化脚本
"""
import sys
import os
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from database.db import init_db

if __name__ == '__main__':
    db_path = os.getenv('DATABASE_PATH', 'data/forum_bot.db')
    
    # 确保数据目录存在
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    
    print(f"正在初始化数据库: {db_path}")
    init_db(db_path)
    print("数据库初始化完成！")
    print("\n默认管理员账户:")
    print("  用户名: admin")
    print("  密码: admin123")
    print("\n请登录后立即修改密码！")
