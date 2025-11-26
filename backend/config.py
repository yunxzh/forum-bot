"""
配置管理模块
"""
import os
from pathlib import Path

class Config:
    """基础配置"""
    BASE_DIR = Path(__file__).resolve().parent.parent
    DATA_DIR = BASE_DIR / 'data'
    LOG_DIR = BASE_DIR / 'logs'
    PRESET_DIR = BASE_DIR / 'presets'
    
    # 确保目录存在
    DATA_DIR.mkdir(exist_ok=True)
    LOG_DIR.mkdir(exist_ok=True)
    
    # 数据库
    DATABASE_PATH = os.getenv('DATABASE_PATH', str(DATA_DIR / 'forum_bot.db'))
    
    # JWT
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'change-this-in-production')
    JWT_ACCESS_TOKEN_EXPIRES = 86400  # 24小时
    
    # 浏览器配置
    CHROME_VERSION = os.getenv('CHROME_VERSION', '')
    HEADLESS = os.getenv('HEADLESS', 'true').lower() == 'true'
    IN_DOCKER = os.getenv('IN_DOCKER', 'false').lower() == 'true'
    
    # Redis (可选，用于任务队列)
    REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    
    # 日志配置
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = LOG_DIR / 'forum_bot.log'

class DevelopmentConfig(Config):
    """开发环境配置"""
    DEBUG = True
    HEADLESS = False

class ProductionConfig(Config):
    """生产环境配置"""
    DEBUG = False
    HEADLESS = True

def get_config():
    """获取配置"""
    env = os.getenv('FLASK_ENV', 'development')
    if env == 'production':
        return ProductionConfig()
    return DevelopmentConfig()
