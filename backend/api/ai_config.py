"""
AI配置API路由
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from datetime import datetime
import json
import logging

from backend.database.db import get_db

bp = Blueprint('ai_config', __name__)
logger = logging.getLogger(__name__)

@bp.route('/config', methods=['GET'])
@jwt_required()
def get_ai_config():
    """获取AI配置"""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM ai_config WHERE id = 1')
            row = cursor.fetchone()
            
            if not row:
                # 返回默认配置
                return jsonify({
                    'provider': 'openai',
                    'base_url': '',
                    'api_key': '',
                    'model': '',
                    'temperature': 0.8,
                    'max_tokens': 100
                })
            
            config = dict(row)
            return jsonify(config)
            
    except Exception as e:
        logger.error(f'获取AI配置失败: {e}', exc_info=True)
        return jsonify({'error': '获取配置失败'}), 500

@bp.route('/config', methods=['PUT'])
@jwt_required()
def update_ai_config():
    """更新AI配置"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': '缺少请求数据'}), 400
        
        provider = data.get('provider', 'openai')
        base_url = data.get('base_url', '')
        api_key = data.get('api_key', '')
        model = data.get('model', '')
        temperature = data.get('temperature', 0.8)
        max_tokens = data.get('max_tokens', 100)
        
        # 验证必填字段
        if not base_url or not api_key or not model:
            return jsonify({'error': '缺少必要的配置参数'}), 400
        
        with get_db() as conn:
            cursor = conn.cursor()
            
            # 检查是否已存在配置
            cursor.execute('SELECT id FROM ai_config WHERE id = 1')
            exists = cursor.fetchone()
            
            if exists:
                # 更新现有配置
                cursor.execute('''
                    UPDATE ai_config 
                    SET provider = ?, base_url = ?, api_key = ?, model = ?,
                        temperature = ?, max_tokens = ?, updated_at = ?
                    WHERE id = 1
                ''', (provider, base_url, api_key, model, temperature, max_tokens, datetime.now()))
            else:
                # 插入新配置
                cursor.execute('''
                    INSERT INTO ai_config (id, provider, base_url, api_key, model, temperature, max_tokens, updated_at)
                    VALUES (1, ?, ?, ?, ?, ?, ?, ?)
                ''', (provider, base_url, api_key, model, temperature, max_tokens, datetime.now()))
            
            conn.commit()
        
        logger.info(f'AI配置已更新: provider={provider}, model={model}')
        return jsonify({'message': 'AI配置已更新'})
        
    except Exception as e:
        logger.error(f'更新AI配置失败: {e}', exc_info=True)
        return jsonify({'error': f'更新配置失败: {str(e)}'}), 500

@bp.route('/config/test', methods=['POST'])
@jwt_required()
def test_ai_config():
    """测试AI配置连接"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': '缺少请求数据'
            }), 400
        
        # 从请求中获取配置参数
        api_key = data.get('api_key', '').strip()
        base_url = data.get('base_url', '').strip()
        model = data.get('model', '').strip()
        temperature = data.get('temperature', 0.8)
        max_tokens = data.get('max_tokens', 50)
        
        # 验证必填参数
        if not all([api_key, base_url, model]):
            return jsonify({
                'success': False,
                'error': '缺少必要的配置参数（API密钥、基础URL或模型名称）'
            }), 400
        
        # 导入 requests 库
        import requests
        
        # 构建请求头
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        
        # 构建请求体
        payload = {
            'model': model,
            'messages': [
                {
                    'role': 'system',
                    'content': '你是一个友好的助手。'
                },
                {
                    'role': 'user',
                    'content': '你好，请回复"测试成功"'
                }
            ],
            'temperature': float(temperature),
            'max_tokens': int(max_tokens)
        }
        
        # 确保 base_url 格式正确
        api_url = base_url.rstrip('/')
        if not api_url.endswith('/chat/completions'):
            api_url += '/chat/completions'
        
        logger.info(f'测试AI连接: URL={api_url}, Model={model}')
        
        # 发送请求到 AI API
        response = requests.post(
            api_url,
            headers=headers,
            json=payload,
            timeout=30
        )
        
        logger.info(f'AI API 响应状态码: {response.status_code}')
        
        # 检查响应状态
        if response.status_code == 200:
            try:
                result = response.json()
                
                # 提取 AI 回复内容
                choices = result.get('choices', [])
                if choices and len(choices) > 0:
                    message = choices[0].get('message', {})
                    reply_content = message.get('content', '')
                    
                    logger.info(f'AI 回复内容: {reply_content}')
                    
                    return jsonify({
                        'success': True,
                        'message': 'AI连接测试成功',
                        'reply': reply_content,
                        'model': result.get('model', model),
                        'usage': result.get('usage', {})
                    })
                else:
                    return jsonify({
                        'success': False,
                        'error': 'AI API 返回格式异常：缺少 choices 字段'
                    }), 400
                    
            except json.JSONDecodeError as e:
                logger.error(f'解析 AI API 响应失败: {e}')
                return jsonify({
                    'success': False,
                    'error': f'解析响应失败: {str(e)}'
                }), 400
        else:
            # API 返回错误状态码
            error_text = response.text
            logger.error(f'AI API 错误 ({response.status_code}): {error_text}')
            
            try:
                error_json = response.json()
                error_message = error_json.get('error', {}).get('message', error_text)
            except:
                error_message = error_text[:200]  # 只取前200个字符
            
            return jsonify({
                'success': False,
                'error': f'API返回错误 (HTTP {response.status_code})',
                'details': error_message
            }), 400
            
    except requests.exceptions.Timeout:
        logger.error('AI API 连接超时')
        return jsonify({
            'success': False,
            'error': '连接超时，请检查网络或API地址是否正确'
        }), 400
        
    except requests.exceptions.ConnectionError as e:
        logger.error(f'无法连接到 AI API: {e}')
        return jsonify({
            'success': False,
            'error': '无法连接到API服务器，请检查Base URL是否正确'
        }), 400
        
    except requests.exceptions.RequestException as e:
        logger.error(f'请求 AI API 失败: {e}')
        return jsonify({
            'success': False,
            'error': f'请求失败: {str(e)}'
        }), 400
        
    except Exception as e:
        logger.error(f'AI配置测试失败: {e}', exc_info=True)
        return jsonify({
            'success': False,
            'error': f'测试失败: {str(e)}'
        }), 500
