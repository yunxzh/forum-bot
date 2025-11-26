"""
Flask 主应用
"""
import os
from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager

# 导入 API 蓝图
from backend.api import auth, sites, tasks, ai_config, notifications
from backend.database.db import init_db

def create_app():
    """创建 Flask 应用"""
    app = Flask(__name__)
    
    # 配置
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-change-in-production')
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'jwt-secret-key-change-in-production')
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = 86400  # 24小时
    
    # CORS 配置
    CORS(app, resources={
        r"/api/*": {
            "origins": "*",
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })
    
    # JWT 初始化
    jwt = JWTManager(app)
    
    # 注册 API 蓝图
    app.register_blueprint(auth.bp, url_prefix='/api/auth')
    app.register_blueprint(sites.bp, url_prefix='/api/sites')
    app.register_blueprint(tasks.bp, url_prefix='/api/tasks')
    app.register_blueprint(ai_config.bp, url_prefix='/api/ai')
    app.register_blueprint(notifications.bp, url_prefix='/api/notifications')
    
    # 健康检查端点
    @app.route('/api/health')
    def health():
        return jsonify({'status': 'ok', 'message': 'Forum-Bot API is running'})
    
    # 根路径
    @app.route('/')
    def index():
        return jsonify({
            'message': 'Forum-Bot API',
            'version': '2.0',
            'status': 'running'
        })
    
    # 错误处理
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Not found'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({'error': 'Internal server error'}), 500
    
    return app

# 创建应用实例
app = create_app()

# ⭐⭐⭐ 关键修复：在应用启动时初始化数据库 ⭐⭐⭐
db_path = os.getenv('DATABASE_PATH', '/app/data/forum_bot.db')

print(f"正在初始化数据库: {db_path}")

try:
    # 检查数据库文件是否存在
    if os.path.exists(db_path):
        print(f"✅ 数据库文件已存在: {db_path}")
    else:
        print(f"📝 创建新数据库: {db_path}")
    
    # 初始化数据库（设置全局 _db_path 变量）
    init_db(db_path)
    print(f"✅ 数据库初始化成功: {db_path}")
    
except Exception as e:
    print(f"❌ 数据库初始化失败: {e}")
    import traceback
    traceback.print_exc()
    # 不退出，尝试继续运行

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('DEBUG', 'False').lower() == 'true'
    
    print(f"启动 Flask 应用...")
    print(f"  - 端口: {port}")
    print(f"  - Debug: {debug}")
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=debug
    )
