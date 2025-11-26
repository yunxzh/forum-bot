"""
认证API路由
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from datetime import datetime
import sqlite3

# 修复导入路径
from backend.database.db import get_db
from backend.models.user import User

bp = Blueprint('auth', __name__)

@bp.route('/login', methods=['POST'])
def login():
    """用户登录"""
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({'error': '用户名和密码不能为空'}), 400
    
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
        row = cursor.fetchone()
        
        if not row:
            return jsonify({'error': '用户名或密码错误'}), 401
        
        user = User(
            id=row['id'],
            username=row['username'],
            password_hash=row['password_hash'],
            created_at=datetime.fromisoformat(row['created_at']) if row['created_at'] else None
        )
        
        if not user.verify_password(password):
            return jsonify({'error': '用户名或密码错误'}), 401
        
        # 更新最后登录时间
        cursor.execute('UPDATE users SET last_login = ? WHERE id = ?', (datetime.now(), user.id))
        conn.commit()
        
        # 创建访问令牌
        access_token = create_access_token(identity=username)
        
        return jsonify({
            'message': '登录成功',
            'access_token': access_token,
            'user': user.to_dict()
        }), 200

@bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """获取当前用户信息"""
    current_username = get_jwt_identity()
    
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE username = ?', (current_username,))
        row = cursor.fetchone()
        
        if not row:
            return jsonify({'error': '用户不存在'}), 404
        
        user = User(
            id=row['id'],
            username=row['username'],
            password_hash=row['password_hash'],
            created_at=datetime.fromisoformat(row['created_at']) if row['created_at'] else None,
            last_login=datetime.fromisoformat(row['last_login']) if row['last_login'] else None
        )
        
        return jsonify(user.to_dict()), 200

@bp.route('/change-password', methods=['POST'])
@jwt_required()
def change_password():
    """修改密码"""
    current_username = get_jwt_identity()
    data = request.get_json()
    
    old_password = data.get('old_password')
    new_password = data.get('new_password')
    
    if not old_password or not new_password:
        return jsonify({'error': '旧密码和新密码不能为空'}), 400
    
    if len(new_password) < 6:
        return jsonify({'error': '新密码长度至少为6位'}), 400
    
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE username = ?', (current_username,))
        row = cursor.fetchone()
        
        if not row:
            return jsonify({'error': '用户不存在'}), 404
        
        user = User(
            id=row['id'],
            username=row['username'],
            password_hash=row['password_hash'],
            created_at=None
        )
        
        if not user.verify_password(old_password):
            return jsonify({'error': '旧密码错误'}), 401
        
        new_password_hash = User.hash_password(new_password)
        cursor.execute('UPDATE users SET password_hash = ? WHERE id = ?', (new_password_hash, user.id))
        conn.commit()
        
        return jsonify({'message': '密码修改成功'}), 200
