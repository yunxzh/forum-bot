"""
通知配置API路由
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from datetime import datetime
import json
import logging

from backend.database.db import get_db
from backend.services.notification_service import NotificationService

bp = Blueprint('notifications', __name__)
logger = logging.getLogger(__name__)

@bp.route('/config', methods=['GET'])
@jwt_required()
def get_notification_config():
    """获取通知配置"""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM notification_config WHERE id = 1')
            row = cursor.fetchone()
            
            if not row:
                # 返回默认配置
                default_config = {
                    'tg_enabled': False,
                    'tg_bot_token': '',
                    'tg_user_id': '',
                    'tg_thread_id': '',
                    'tg_api_host': 'https://api.telegram.org',
                    'tg_proxy_host': '',
                    'tg_proxy_port': '',
                    'wecom_enabled': False,
                    'wecom_key': '',
                    'pushplus_enabled': False,
                    'pushplus_token': '',
                    'pushplus_user': '',
                    'dingding_enabled': False,
                    'dingding_token': '',
                    'dingding_secret': '',
                    'feishu_enabled': False,
                    'feishu_key': '',
                    'bark_enabled': False,
                    'bark_push': '',
                    'bark_sound': '',
                    'smtp_enabled': False,
                    'smtp_server': '',
                    'smtp_port': 465,
                    'smtp_ssl': True,
                    'smtp_email': '',
                    'smtp_password': '',
                    'smtp_name': 'Forum-Bot',
                    'gotify_enabled': False,
                    'gotify_url': '',
                    'gotify_token': '',
                    'gotify_priority': 5
                }
                return jsonify(default_config)
            
            config_json = json.loads(row['config_json'])
            return jsonify(config_json)
            
    except Exception as e:
        logger.error(f'获取通知配置失败: {e}', exc_info=True)
        return jsonify({'error': '获取配置失败'}), 500

@bp.route('/config', methods=['PUT'])
@jwt_required()
def update_notification_config():
    """更新通知配置"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': '缺少请求数据'}), 400
        
        # 将配置转换为 JSON 字符串
        config_json = json.dumps(data, ensure_ascii=False)
        
        with get_db() as conn:
            cursor = conn.cursor()
            
            # 检查是否已存在配置
            cursor.execute('SELECT id FROM notification_config WHERE id = 1')
            exists = cursor.fetchone()
            
            if exists:
                # 更新现有配置
                cursor.execute('''
                    UPDATE notification_config 
                    SET config_json = ?, updated_at = ?
                    WHERE id = 1
                ''', (config_json, datetime.now()))
            else:
                # 插入新配置
                cursor.execute('''
                    INSERT INTO notification_config (id, config_json, updated_at)
                    VALUES (1, ?, ?)
                ''', (config_json, datetime.now()))
            
            conn.commit()
        
        logger.info('通知配置已更新')
        return jsonify({'message': '通知配置已更新'})
        
    except Exception as e:
        logger.error(f'更新通知配置失败: {e}', exc_info=True)
        return jsonify({'error': f'更新配置失败: {str(e)}'}), 500

@bp.route('/test', methods=['POST'])
@jwt_required()
def test_notification():
    """测试通知发送"""
    try:
        data = request.get_json()
        
        logger.info(f'收到测试通知请求: {data}')
        
        if not data:
            data = {}
        
        channel = data.get('channel', 'all')
        
        # 创建通知服务实例
        notification_service = NotificationService()
        
        # 发送测试通知
        title = "Forum-Bot 测试通知"
        content = f"这是一条测试通知\n发送时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        results = {}
        
        try:
            # 确保配置已加载
            notification_service._ensure_config_loaded()
            
            if channel == 'all' or channel == 'telegram':
                if notification_service.config and notification_service.config.tg_enabled:
                    logger.info('发送 Telegram 测试通知')
                    result = notification_service._send_telegram(title, content)
                    results['telegram'] = {
                        'success': result,
                        'message': '发送成功' if result else '发送失败'
                    }
            
            if channel == 'all' or channel == 'wecom':
                if notification_service.config and notification_service.config.wecom_enabled:
                    result = notification_service._send_wecom(title, content)
                    results['wecom'] = {
                        'success': result,
                        'message': '发送成功' if result else '发送失败'
                    }
            
            if channel == 'all' or channel == 'pushplus':
                if notification_service.config and notification_service.config.pushplus_enabled:
                    logger.info('发送 PushPlus 测试通知')
                    result = notification_service._send_pushplus(title, content)
                    results['pushplus'] = {
                        'success': result,
                        'message': '发送成功' if result else '发送失败'
                    }
            
            if channel == 'all' or channel == 'dingding':
                if notification_service.config and notification_service.config.dingding_enabled:
                    result = notification_service._send_dingding(title, content)
                    results['dingding'] = {
                        'success': result,
                        'message': '发送成功' if result else '发送失败'
                    }
            
            if channel == 'all' or channel == 'feishu':
                if notification_service.config and notification_service.config.feishu_enabled:
                    result = notification_service._send_feishu(title, content)
                    results['feishu'] = {
                        'success': result,
                        'message': '发送成功' if result else '发送失败'
                    }
            
            if channel == 'all' or channel == 'bark':
                if notification_service.config and notification_service.config.bark_enabled:
                    result = notification_service._send_bark(title, content)
                    results['bark'] = {
                        'success': result,
                        'message': '发送成功' if result else '发送失败'
                    }
            
            if channel == 'all' or channel == 'smtp':
                if notification_service.config and notification_service.config.smtp_enabled:
                    result = notification_service._send_smtp(title, content)
                    results['smtp'] = {
                        'success': result,
                        'message': '发送成功' if result else '发送失败'
                    }
            
            if channel == 'all' or channel == 'gotify':
                if notification_service.config and notification_service.config.gotify_enabled:
                    result = notification_service._send_gotify(title, content)
                    results['gotify'] = {
                        'success': result,
                        'message': '发送成功' if result else '发送失败'
                    }
            
        except Exception as send_error:
            logger.error(f'发送通知时出错: {send_error}', exc_info=True)
            return jsonify({
                'success': False,
                'error': f'发送失败: {str(send_error)}'
            }), 500
        
        if not results:
            return jsonify({
                'success': False,
                'error': '没有启用任何通知渠道'
            }), 400
        
        # 检查是否有成功的发送
        any_success = any(r.get('success', False) for r in results.values())
        
        logger.info(f'测试通知结果: {results}')
        
        return jsonify({
            'success': any_success,
            'message': '测试通知已发送' if any_success else '所有通知发送失败',
            'results': results
        })
        
    except Exception as e:
        logger.error(f'测试通知失败: {e}', exc_info=True)
        return jsonify({
            'success': False,
            'error': f'测试失败: {str(e)}'
        }), 500
