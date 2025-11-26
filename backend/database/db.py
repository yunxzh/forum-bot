"""
数据库管理模块
"""
import sqlite3
from contextlib import contextmanager
from typing import Optional
import json
from datetime import datetime

_db_path: Optional[str] = None

def init_db(db_path: str):
    """初始化数据库"""
    global _db_path
    _db_path = db_path
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 创建用户表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP
        )
    ''')
    
    # 创建站点表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sites (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            base_url TEXT NOT NULL,
            cron_expression TEXT NOT NULL,
            preset_template TEXT,
            auth_type TEXT DEFAULT 'cookie',
            cookie_string TEXT,
            username TEXT,
            password TEXT,
            selectors TEXT,
            enable_signin INTEGER DEFAULT 1,
            enable_reply INTEGER DEFAULT 1,
            enable_feedback INTEGER DEFAULT 1,
            max_daily_replies INTEGER DEFAULT 20,
            reply_interval_min INTEGER DEFAULT 60,
            reply_interval_max INTEGER DEFAULT 300,
            min_reply_count INTEGER DEFAULT 1,
            max_reply_count INTEGER DEFAULT 10,
            reply_randomness REAL DEFAULT 0.8,
            http_proxy TEXT,
            user_agent TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_run_at TIMESTAMP,
            is_active INTEGER DEFAULT 1
        )
    ''')
    
    # 创建任务日志表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS task_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            site_id INTEGER NOT NULL,
            task_type TEXT NOT NULL,
            status TEXT NOT NULL,
            message TEXT,
            details TEXT,
            executed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            duration REAL,
            FOREIGN KEY (site_id) REFERENCES sites(id) ON DELETE CASCADE
        )
    ''')
    
    # 创建AI配置表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ai_config (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            provider TEXT DEFAULT 'openai',
            base_url TEXT NOT NULL,
            api_key TEXT NOT NULL,
            model TEXT NOT NULL,
            temperature REAL DEFAULT 0.8,
            max_tokens INTEGER DEFAULT 100,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 创建通知配置表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS notification_config (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            config_json TEXT NOT NULL,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 创建索引
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_task_logs_site_id ON task_logs(site_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_task_logs_executed_at ON task_logs(executed_at)')
    
    conn.commit()
    
    # 创建默认管理员账户（如果不存在）
    # 修复：使用绝对导入路径
    from backend.models.user import User
    cursor.execute('SELECT COUNT(*) FROM users')
    if cursor.fetchone()[0] == 0:
        default_password_hash = User.hash_password('admin123')
        cursor.execute(
            'INSERT INTO users (username, password_hash) VALUES (?, ?)',
            ('admin', default_password_hash)
        )
        conn.commit()
        print("创建默认管理员账户: admin / admin123")
    
    conn.close()
    print(f"数据库初始化完成: {db_path}")

@contextmanager
def get_db():
    """获取数据库连接上下文管理器"""
    if _db_path is None:
        raise RuntimeError("数据库未初始化，请先调用 init_db()")
    
    conn = sqlite3.connect(_db_path)
    conn.row_factory = sqlite3.Row  # 返回字典形式的行
    try:
        yield conn
    finally:
        conn.close()

def dict_factory(cursor, row):
    """将查询结果转换为字典"""
    return {col[0]: row[idx] for idx, col in enumerate(cursor.description)}
