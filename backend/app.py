"""
Forum-Bot Web 管理后台主应用
使用 Flask + Flask-CORS + Flask-JWT-Extended
"""
from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from datetime import timedelta
import os

from database.db import init_db, get_db
from api import auth, sites, tasks, ai_config, notifications

app = Flask(__name__)

# 配置
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'forum-bot-secret-key-change-in-production')
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'jwt-secret-key-change-in-production')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)
app.config['DATABASE_PATH'] = os.getenv('DATABASE_PATH', 'data/forum_bot.db')

# 初始化扩展
CORS(app, resources={r"/api/*": {"origins": "*"}})
jwt = JWTManager(app)

# 注册蓝图
app.register_blueprint(auth.bp, url_prefix='/api/auth')
app.register_blueprint(sites.bp, url_prefix='/api/sites')
app.register_blueprint(tasks.bp, url_prefix='/api/tasks')
app.register_blueprint(ai_config.bp, url_prefix='/api/ai')
app.register_blueprint(notifications.bp, url_prefix='/api/notifications')

# 初始化数据库
with app.app_context():
    init_db(app.config['DATABASE_PATH'])

@app.route('/api/health', methods=['GET'])
def health_check():
    """健康检查"""
    return jsonify({'status': 'ok', 'message': 'Forum-Bot API is running'}), 200

@app.route('/api/version', methods=['GET'])
def version():
    """版本信息"""
    return jsonify({
        'version': '2.0.0',
        'name': 'Forum-Bot',
        'description': '通用论坛自动化机器人平台'
    }), 200

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('DEBUG', 'False').lower() == 'true'
    app.run(host='0.0.0.0', port=port, debug=debug)
