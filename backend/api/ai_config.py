"""
AI配置API路由
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from datetime import datetime

from database.db import get_db

bp = Blueprint('ai', __name__)

@bp.route('/config', methods=['GET'])
@jwt_required()
def get_ai_config():
    """获取AI配置"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM ai_config WHERE id = 1')
        row = cursor.fetchone()
        
        if not row:
            # 返回默认配置
            return jsonify({
                'provider': 'openai',
                'base_url': 'https://api.openai.com/v1',
                'api_key': '',
                'model': 'gpt-3.5-turbo',
                'temperature': 0.8,
                'max_tokens': 100
            }), 200
        
        config = dict(row)
        # 隐藏API密钥
        config['api_key'] = '******' if config['api_key'] else ''
        
        return jsonify(config), 200

@bp.route('/config', methods=['PUT'])
@jwt_required()
def update_ai_config():
    """更新AI配置"""
    data = request.get_json()
    
    required_fields = ['base_url', 'api_key', 'model']
    for field in required_fields:
        if field not in data or not data[field]:
            return jsonify({'error': f'缺少必填字段: {field}'}), 400
    
    with get_db() as conn:
        cursor = conn.cursor()
        
        # 检查是否已存在配置
        cursor.execute('SELECT * FROM ai_config WHERE id = 1')
        exists = cursor.fetchone()
        
        if exists:
            # 更新配置
            cursor.execute('''
                UPDATE ai_config SET
                    provider = ?,
                    base_url = ?,
                    api_key = ?,
                    model = ?,
                    temperature = ?,
                    max_tokens = ?,
                    updated_at = ?
                WHERE id = 1
            ''', (
                data.get('provider', 'openai'),
                data['base_url'],
                data['api_key'],
                data['model'],
                data.get('temperature', 0.8),
                data.get('max_tokens', 100),
                datetime.now()
            ))
        else:
            # 插入新配置
            cursor.execute('''
                INSERT INTO ai_config (
                    id, provider, base_url, api_key, model,
                    temperature, max_tokens
                ) VALUES (1, ?, ?, ?, ?, ?, ?)
            ''', (
                data.get('provider', 'openai'),
                data['base_url'],
                data['api_key'],
                data['model'],
                data.get('temperature', 0.8),
                data.get('max_tokens', 100)
            ))
        
        conn.commit()
        
        return jsonify({'message': 'AI配置更新成功'}), 200

@bp.route('/config/test', methods=['POST'])
@jwt_required()
def test_ai_config():
    """测试AI配置"""
    data = request.get_json()
    
    # TODO: 实现AI配置测试逻辑
    # 应该尝试调用AI API来验证配置是否正确
    
    return jsonify({'message': 'AI配置测试功能开发中'}), 501
