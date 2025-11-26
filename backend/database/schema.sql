-- Forum-Bot 数据库设计
-- SQLite 数据库

-- 用户表
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP
);

-- 站点表
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
    selectors TEXT,  -- JSON格式存储
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
);

-- 任务日志表
CREATE TABLE IF NOT EXISTS task_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    site_id INTEGER NOT NULL,
    task_type TEXT NOT NULL,  -- signin, reply, feedback
    status TEXT NOT NULL,      -- success, failed, skipped
    message TEXT,
    details TEXT,              -- JSON格式存储详细信息
    executed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    duration REAL,             -- 执行耗时（秒）
    FOREIGN KEY (site_id) REFERENCES sites(id) ON DELETE CASCADE
);

-- AI配置表
CREATE TABLE IF NOT EXISTS ai_config (
    id INTEGER PRIMARY KEY CHECK (id = 1),  -- 单例模式
    provider TEXT DEFAULT 'openai',
    base_url TEXT NOT NULL,
    api_key TEXT NOT NULL,
    model TEXT NOT NULL,
    temperature REAL DEFAULT 0.8,
    max_tokens INTEGER DEFAULT 100,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 通知配置表
CREATE TABLE IF NOT EXISTS notification_config (
    id INTEGER PRIMARY KEY CHECK (id = 1),  -- 单例模式
    config_json TEXT NOT NULL,              -- JSON格式存储所有通知配置
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_task_logs_site_id ON task_logs(site_id);
CREATE INDEX IF NOT EXISTS idx_task_logs_executed_at ON task_logs(executed_at);
CREATE INDEX IF NOT EXISTS idx_sites_is_active ON sites(is_active);

-- 插入默认管理员账户
-- 密码: admin123 (已哈希)
INSERT OR IGNORE INTO users (id, username, password_hash) 
VALUES (1, 'admin', '$2b$12$默认哈希值会在代码中生成');
