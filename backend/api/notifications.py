"""
通知配置API路由
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from datetime import datetime
import json

from database.db import get_db
from models.notification import NotificationConfig

bp = Blueprint('notifications', __name__)

@bp.route('/config', methods=['GET'])
@jwt_required()
def get_notification_config():
    """获取通知配置"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM notification_config WHERE id = 1')
        row = cursor.fetchone()
        
        if not row:
            # 返回默认配置
            return jsonify(NotificationConfig().to_dict()), 200
        
        config_json = json.loads(row['config_json'])
        config = NotificationConfig.from_dict(config_json)
        
        return jsonify(config.to_dict()), 200

@bp.route('/config', methods=['PUT'])
@jwt_required()
def update_notification_config():
    """更新通知配置"""
    data = request.get_json()
    
    config = NotificationConfig.from_dict(data)
    config_json = json.dumps(config.to_full_dict())
    
    with get_db() as conn:
        cursor = conn.cursor()
        
        # 检查是否已存在配置
        cursor.execute('SELECT * FROM notification_config WHERE id = 1')
        exists = cursor.fetchone()
        
        if exists:
            cursor.execute('''
                UPDATE notification_config SET
                    config_json = ?,
                    updated_at = ?
                WHERE id = 1
            ''', (config_json, datetime.now()))
        else:
            cursor.execute('''
                INSERT INTO notification_config (id, config_json)
                VALUES (1, ?)
            ''', (config_json,))
        
        conn.commit()
        
        return jsonify({'message': '通知配置更新成功'}), 200

@bp.route('/test', methods=['POST'])
@jwt_required()
def test_notification():
    """测试通知发送"""
    data = request.get_json()
    channel = data.get('channel')  # telegram, wecom, pushplus, etc.
    
    if not channel:
        return jsonify({'error': '请指定通知渠道'}), 400
    
    # TODO: 实现通知测试逻辑
    # 应该调用对应的通知服务发送测试消息
    
    return jsonify({'message': f'{channel} 通知测试功能开发中'}), 501
