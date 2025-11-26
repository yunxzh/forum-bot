"""
通知配置模型
"""
from dataclasses import dataclass, field
from typing import Optional, Dict, Any
import json

@dataclass
class NotificationConfig:
    id: Optional[int] = None
    
    # Telegram
    tg_enabled: bool = False
    tg_bot_token: Optional[str] = None
    tg_user_id: Optional[str] = None
    tg_thread_id: Optional[str] = None
    tg_api_host: str = 'https://api.telegram.org'
    tg_proxy_host: Optional[str] = None
    tg_proxy_port: Optional[str] = None
    
    # 企业微信机器人
    wecom_enabled: bool = False
    wecom_key: Optional[str] = None
    
    # PushPlus
    pushplus_enabled: bool = False
    pushplus_token: Optional[str] = None
    pushplus_user: Optional[str] = None
    
    # 钉钉机器人
    dingding_enabled: bool = False
    dingding_token: Optional[str] = None
    dingding_secret: Optional[str] = None
    
    # 飞书机器人
    feishu_enabled: bool = False
    feishu_key: Optional[str] = None
    
    # Bark
    bark_enabled: bool = False
    bark_push: Optional[str] = None
    bark_sound: Optional[str] = None
    
    # SMTP 邮件
    smtp_enabled: bool = False
    smtp_server: Optional[str] = None
    smtp_port: int = 465
    smtp_ssl: bool = True
    smtp_email: Optional[str] = None
    smtp_password: Optional[str] = None
    smtp_name: Optional[str] = None
    
    # Gotify
    gotify_enabled: bool = False
    gotify_url: Optional[str] = None
    gotify_token: Optional[str] = None
    gotify_priority: int = 5
    
    def to_dict(self) -> dict:
        """转换为字典（用于存储和API返回）"""
        result = {}
        for key, value in self.__dict__.items():
            if key == 'id':
                continue
            # 隐藏敏感信息
            if 'password' in key or 'token' in key or 'secret' in key or 'key' in key:
                result[key] = '******' if value else None
            else:
                result[key] = value
        return result
    
    def to_full_dict(self) -> dict:
        """转换为完整字典（包含敏感信息，用于内部使用）"""
        return {k: v for k, v in self.__dict__.items() if k != 'id'}
    
    @classmethod
    def from_dict(cls, data: dict) -> 'NotificationConfig':
        """从字典创建"""
        return cls(**{k: v for k, v in data.items() if k in cls.__annotations__})
