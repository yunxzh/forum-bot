"""
通知服务
整合原有的 notify.py 功能
"""
import json
import requests
import time
import hmac
import hashlib
import base64
import urllib.parse
from typing import Optional
from datetime import datetime
import logging

from backend.database.db import get_db
from backend.models.notification import NotificationConfig

logger = logging.getLogger(__name__)

class NotificationService:
    def __init__(self):
        self.config = None  # 延迟加载
        self._config_loaded = False
    
    def _ensure_config_loaded(self):
        """确保配置已加载"""
        if not self._config_loaded:
            self.config = self._load_config()
            self._config_loaded = True
            logger.info(f'通知配置已加载: {self.config}')
    
    def _load_config(self) -> NotificationConfig:
        """加载通知配置"""
        try:
            with get_db() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM notification_config WHERE id = 1')
                row = cursor.fetchone()
                
                if not row:
                    logger.warning('未找到通知配置，使用默认配置')
                    return NotificationConfig()
                
                config_json = json.loads(row['config_json'])
                logger.info(f'从数据库加载的配置: {config_json}')
                
                return NotificationConfig.from_dict(config_json)
        except Exception as e:
            logger.warning(f"加载通知配置失败: {e}，使用默认配置")
            return NotificationConfig()
    
    def send(self, title: str, content: str):
        """发送通知到所有已启用的渠道"""
        self._ensure_config_loaded()  # 确保配置已加载
        
        if not self.config:
            logger.warning("通知配置未加载，跳过发送")
            return {}
        
        results = {}
        
        if self.config.tg_enabled:
            logger.info('Telegram 已启用，尝试发送')
            results['telegram'] = self._send_telegram(title, content)
        
        if self.config.wecom_enabled:
            logger.info('企业微信已启用，尝试发送')
            results['wecom'] = self._send_wecom(title, content)
        
        if self.config.pushplus_enabled:
            logger.info('PushPlus 已启用，尝试发送')
            results['pushplus'] = self._send_pushplus(title, content)
        
        if self.config.dingding_enabled:
            logger.info('钉钉已启用，尝试发送')
            results['dingding'] = self._send_dingding(title, content)
        
        if self.config.feishu_enabled:
            logger.info('飞书已启用，尝试发送')
            results['feishu'] = self._send_feishu(title, content)
        
        if self.config.bark_enabled:
            logger.info('Bark 已启用，尝试发送')
            results['bark'] = self._send_bark(title, content)
        
        if self.config.smtp_enabled:
            logger.info('SMTP 已启用，尝试发送')
            results['smtp'] = self._send_smtp(title, content)
        
        if self.config.gotify_enabled:
            logger.info('Gotify 已启用，尝试发送')
            results['gotify'] = self._send_gotify(title, content)
        
        return results
    
    def _send_telegram(self, title: str, content: str) -> bool:
        """发送Telegram通知"""
        if not self.config.tg_bot_token or not self.config.tg_user_id:
            logger.warning('Telegram 配置不完整')
            return False
        
        try:
            url = f"{self.config.tg_api_host}/bot{self.config.tg_bot_token}/sendMessage"
            
            payload = {
                'chat_id': self.config.tg_user_id,
                'text': f"*{title}*\n\n{content}",
                'parse_mode': 'Markdown',
                'disable_web_page_preview': True
            }
            
            if self.config.tg_thread_id:
                payload['message_thread_id'] = self.config.tg_thread_id
            
            proxies = None
            if self.config.tg_proxy_host and self.config.tg_proxy_port:
                proxy_url = f"http://{self.config.tg_proxy_host}:{self.config.tg_proxy_port}"
                proxies = {'http': proxy_url, 'https': proxy_url}
            
            response = requests.post(url, json=payload, proxies=proxies, timeout=15)
            success = response.status_code == 200
            
            if success:
                logger.info('Telegram 通知发送成功')
            else:
                logger.error(f'Telegram 通知发送失败: {response.text}')
            
            return success
        except Exception as e:
            logger.error(f"Telegram通知发送失败: {e}", exc_info=True)
            return False
    
    def _send_wecom(self, title: str, content: str) -> bool:
        """发送企业微信机器人通知"""
        if not self.config.wecom_key:
            return False
        
        try:
            url = f"https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key={self.config.wecom_key}"
            data = {
                'msgtype': 'text',
                'text': {'content': f"{title}\n\n{content}"}
            }
            response = requests.post(url, json=data, timeout=15)
            return response.json().get('errcode') == 0
        except Exception as e:
            logger.error(f"企业微信通知发送失败: {e}")
            return False
    
    def _send_pushplus(self, title: str, content: str) -> bool:
        """发送PushPlus通知"""
        if not self.config.pushplus_token:
            logger.warning('PushPlus Token 未配置')
            return False
        
        try:
            url = "http://www.pushplus.plus/send"
            data = {
                'token': self.config.pushplus_token,
                'title': title,
                'content': content,
                'template': 'html'
            }
            
            if self.config.pushplus_user:
                data['topic'] = self.config.pushplus_user
            
            logger.info(f'发送 PushPlus 通知到: {url}')
            response = requests.post(url, json=data, timeout=15)
            result = response.json()
            success = result.get('code') == 200
            
            if success:
                logger.info('PushPlus 通知发送成功')
            else:
                logger.error(f'PushPlus 通知发送失败: {result}')
            
            return success
        except Exception as e:
            logger.error(f"PushPlus通知发送失败: {e}", exc_info=True)
            return False
    
    def _send_dingding(self, title: str, content: str) -> bool:
        """发送钉钉机器人通知"""
        if not self.config.dingding_token or not self.config.dingding_secret:
            return False
        
        try:
            timestamp = str(round(time.time() * 1000))
            secret_enc = self.config.dingding_secret.encode('utf-8')
            string_to_sign = f"{timestamp}\n{self.config.dingding_secret}"
            string_to_sign_enc = string_to_sign.encode('utf-8')
            hmac_code = hmac.new(secret_enc, string_to_sign_enc, digestmod=hashlib.sha256).digest()
            sign = urllib.parse.quote_plus(base64.b64encode(hmac_code))
            
            url = f"https://oapi.dingtalk.com/robot/send?access_token={self.config.dingding_token}&timestamp={timestamp}&sign={sign}"
            data = {
                'msgtype': 'text',
                'text': {'content': f"{title}\n\n{content}"}
            }
            response = requests.post(url, json=data, timeout=15)
            return response.json().get('errcode') == 0
        except Exception as e:
            logger.error(f"钉钉通知发送失败: {e}")
            return False
    
    def _send_feishu(self, title: str, content: str) -> bool:
        """发送飞书机器人通知"""
        if not self.config.feishu_key:
            return False
        
        try:
            url = f"https://open.feishu.cn/open-apis/bot/v2/hook/{self.config.feishu_key}"
            data = {
                'msg_type': 'text',
                'content': {'text': f"{title}\n\n{content}"}
            }
            response = requests.post(url, json=data, timeout=15)
            return response.json().get('code') == 0
        except Exception as e:
            logger.error(f"飞书通知发送失败: {e}")
            return False
    
    def _send_bark(self, title: str, content: str) -> bool:
        """发送Bark通知"""
        if not self.config.bark_push:
            return False
        
        try:
            if self.config.bark_push.startswith('http'):
                url = f"{self.config.bark_push}/{urllib.parse.quote_plus(title)}/{urllib.parse.quote_plus(content)}"
            else:
                url = f"https://api.day.app/{self.config.bark_push}/{urllib.parse.quote_plus(title)}/{urllib.parse.quote_plus(content)}"
            
            params = {}
            if self.config.bark_sound:
                params['sound'] = self.config.bark_sound
            
            response = requests.get(url, params=params, timeout=15)
            return response.json().get('code') == 200
        except Exception as e:
            logger.error(f"Bark通知发送失败: {e}")
            return False
    
    def _send_smtp(self, title: str, content: str) -> bool:
        """发送SMTP邮件通知"""
        if not self.config.smtp_server or not self.config.smtp_email or not self.config.smtp_password:
            return False
        
        try:
            import smtplib
            from email.mime.text import MIMEText
            from email.header import Header
            
            message = MIMEText(content, 'plain', 'utf-8')
            message['From'] = Header(self.config.smtp_name or 'Forum-Bot', 'utf-8')
            message['To'] = Header(self.config.smtp_email, 'utf-8')
            message['Subject'] = Header(title, 'utf-8')
            
            server_parts = self.config.smtp_server.split(':')
            server_host = server_parts[0]
            server_port = int(server_parts[1]) if len(server_parts) > 1 else (465 if self.config.smtp_ssl else 25)
            
            if self.config.smtp_ssl:
                server = smtplib.SMTP_SSL(server_host, server_port)
            else:
                server = smtplib.SMTP(server_host, server_port)
            
            server.login(self.config.smtp_email, self.config.smtp_password)
            server.sendmail(self.config.smtp_email, [self.config.smtp_email], message.as_string())
            server.quit()
            return True
        except Exception as e:
            logger.error(f"SMTP通知发送失败: {e}")
            return False
    
    def _send_gotify(self, title: str, content: str) -> bool:
        """发送Gotify通知"""
        if not self.config.gotify_url or not self.config.gotify_token:
            return False
        
        try:
            url = f"{self.config.gotify_url}/message?token={self.config.gotify_token}"
            data = {
                'title': title,
                'message': content,
                'priority': self.config.gotify_priority
            }
            response = requests.post(url, json=data, timeout=15)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Gotify通知发送失败: {e}")
            return False

    def is_any_enabled(self) -> bool:
        """检查是否有任何通知渠道被启用"""
        self._ensure_config_loaded()  # 确保配置已加载
        
        if not self.config:
            return False
        
        enabled = any([
            self.config.tg_enabled,
            self.config.wecom_enabled,
            self.config.pushplus_enabled,
            self.config.dingding_enabled,
            self.config.feishu_enabled,
            self.config.bark_enabled,
            self.config.smtp_enabled,
            self.config.gotify_enabled
        ])
        
        logger.info(f'是否有启用的通知渠道: {enabled}')
        logger.info(f'配置详情 - TG: {self.config.tg_enabled}, PushPlus: {self.config.pushplus_enabled}')
        
        return enabled
