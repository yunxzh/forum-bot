"""
站点管理API路由
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from datetime import datetime
import json
import os
from pathlib import Path

# 修复导入路径
from backend.database.db import get_db
from backend.models.site import Site

bp = Blueprint('sites', __name__)

@bp.route('', methods=['GET'])
@jwt_required()
def list_sites():
    """获取所有站点列表"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM sites ORDER BY created_at DESC')
        rows = cursor.fetchall()
        
        sites = []
        for row in rows:
            site_dict = dict(row)
            # 解析 JSON 字段
            if site_dict.get('selectors'):
                site_dict['selectors'] = json.loads(site_dict['selectors'])
            sites.append(site_dict)
        
        return jsonify(sites), 200

@bp.route('/<int:site_id>', methods=['GET'])
@jwt_required()
def get_site(site_id):
    """获取单个站点详情"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM sites WHERE id = ?', (site_id,))
        row = cursor.fetchone()
        
        if not row:
            return jsonify({'error': '站点不存在'}), 404
        
        site_dict = dict(row)
        if site_dict.get('selectors'):
            site_dict['selectors'] = json.loads(site_dict['selectors'])
        
        return jsonify(site_dict), 200

@bp.route('', methods=['POST'])
@jwt_required()
def create_site():
    """创建新站点"""
    data = request.get_json()
    
    # 验证必填字段
    required_fields = ['name', 'base_url', 'cron_expression', 'auth_type']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'缺少必填字段: {field}'}), 400
    
    # 验证认证方式
    if data['auth_type'] == 'cookie' and not data.get('cookie_string'):
        return jsonify({'error': 'Cookie登录方式需要提供cookie_string'}), 400
    elif data['auth_type'] == 'password' and (not data.get('username') or not data.get('password')):
        return jsonify({'error': '账号密码登录方式需要提供username和password'}), 400
    
    with get_db() as conn:
        cursor = conn.cursor()
        
        # 检查站点名称是否已存在
        cursor.execute('SELECT COUNT(*) FROM sites WHERE name = ?', (data['name'],))
        if cursor.fetchone()[0] > 0:
            return jsonify({'error': '站点名称已存在'}), 400
        
        # 插入新站点
        selectors_json = json.dumps(data.get('selectors', {}))
        
        cursor.execute('''
            INSERT INTO sites (
                name, base_url, cron_expression, preset_template,
                auth_type, cookie_string, username, password,
                selectors, enable_signin, enable_reply, enable_feedback,
                max_daily_replies, reply_interval_min, reply_interval_max,
                min_reply_count, max_reply_count, reply_randomness,
                http_proxy, user_agent, is_active
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data['name'],
            data['base_url'],
            data['cron_expression'],
            data.get('preset_template'),
            data['auth_type'],
            data.get('cookie_string'),
            data.get('username'),
            data.get('password'),
            selectors_json,
            data.get('enable_signin', True),
            data.get('enable_reply', True),
            data.get('enable_feedback', True),
            data.get('max_daily_replies', 20),
            data.get('reply_interval_min', 60),
            data.get('reply_interval_max', 300),
            data.get('min_reply_count', 1),
            data.get('max_reply_count', 10),
            data.get('reply_randomness', 0.8),
            data.get('http_proxy'),
            data.get('user_agent'),
            data.get('is_active', True)
        ))
        
        conn.commit()
        site_id = cursor.lastrowid
        
        return jsonify({'message': '站点创建成功', 'id': site_id}), 201

@bp.route('/<int:site_id>', methods=['PUT'])
@jwt_required()
def update_site(site_id):
    """更新站点配置"""
    data = request.get_json()
    
    with get_db() as conn:
        cursor = conn.cursor()
        
        # 检查站点是否存在
        cursor.execute('SELECT * FROM sites WHERE id = ?', (site_id,))
        if not cursor.fetchone():
            return jsonify({'error': '站点不存在'}), 404
        
        # 构建更新SQL
        update_fields = []
        update_values = []
        
        allowed_fields = [
            'name', 'base_url', 'cron_expression', 'preset_template',
            'auth_type', 'cookie_string', 'username', 'password',
            'enable_signin', 'enable_reply', 'enable_feedback',
            'max_daily_replies', 'reply_interval_min', 'reply_interval_max',
            'min_reply_count', 'max_reply_count', 'reply_randomness',
            'http_proxy', 'user_agent', 'is_active'
        ]
        
        for field in allowed_fields:
            if field in data:
                update_fields.append(f'{field} = ?')
                update_values.append(data[field])
        
        # 处理 selectors
        if 'selectors' in data:
            update_fields.append('selectors = ?')
            update_values.append(json.dumps(data['selectors']))
        
        # 添加更新时间
        update_fields.append('updated_at = ?')
        update_values.append(datetime.now())
        
        # 添加站点ID
        update_values.append(site_id)
        
        sql = f"UPDATE sites SET {', '.join(update_fields)} WHERE id = ?"
        cursor.execute(sql, update_values)
        conn.commit()
        
        return jsonify({'message': '站点更新成功'}), 200

@bp.route('/<int:site_id>', methods=['DELETE'])
@jwt_required()
def delete_site(site_id):
    """删除站点"""
    with get_db() as conn:
        cursor = conn.cursor()
        
        # 检查站点是否存在
        cursor.execute('SELECT * FROM sites WHERE id = ?', (site_id,))
        if not cursor.fetchone():
            return jsonify({'error': '站点不存在'}), 404
        
        # 删除站点（级联删除相关任务日志）
        cursor.execute('DELETE FROM sites WHERE id = ?', (site_id,))
        conn.commit()
        
        return jsonify({'message': '站点删除成功'}), 200

@bp.route('/presets', methods=['GET'])
@jwt_required()
def get_presets():
    """获取预设模板列表"""
    preset_dir = Path(__file__).resolve().parent.parent.parent / 'presets'
    
    presets = []
    if preset_dir.exists():
        for preset_file in preset_dir.glob('*.json'):
            try:
                with open(preset_file, 'r', encoding='utf-8') as f:
                    preset_data = json.load(f)
                    presets.append({
                        'id': preset_file.stem,
                        'name': preset_data.get('name', preset_file.stem),
                        'architecture': preset_data.get('architecture', 'Unknown')
                    })
            except Exception as e:
                print(f"读取预设文件失败 {preset_file}: {e}")
    
    return jsonify(presets), 200

@bp.route('/presets/<preset_id>', methods=['GET'])
@jwt_required()
def get_preset_detail(preset_id):
    """获取预设模板详情"""
    preset_dir = Path(__file__).resolve().parent.parent.parent / 'presets'
    preset_file = preset_dir / f'{preset_id}.json'
    
    if not preset_file.exists():
        return jsonify({'error': '预设模板不存在'}), 404
    
    try:
        with open(preset_file, 'r', encoding='utf-8') as f:
            preset_data = json.load(f)
        return jsonify(preset_data), 200
    except Exception as e:
        return jsonify({'error': f'读取预设模板失败: {str(e)}'}), 500

@bp.route('/<int:site_id>/test', methods=['POST'])
@jwt_required()
def test_site_connection(site_id):
    """测试站点连接"""
    # TODO: 实现站点连接测试逻辑
    return jsonify({'message': '连接测试功能开发中'}), 501
