"""
站点模型
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, Any
import json

@dataclass
class Site:
    id: Optional[int]
    name: str
    base_url: str
    cron_expression: str
    preset_template: Optional[str] = None
    
    # 登录配置
    auth_type: str = 'cookie'  # 'cookie' 或 'password'
    cookie_string: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    
    # CSS 选择器配置
    selectors: Dict[str, Any] = field(default_factory=dict)
    
    # 任务开关
    enable_signin: bool = True
    enable_reply: bool = True
    enable_feedback: bool = True
    
    # 回复策略
    max_daily_replies: int = 20
    reply_interval_min: int = 60
    reply_interval_max: int = 300
    min_reply_count: int = 1
    max_reply_count: int = 10
    reply_randomness: float = 0.8
    
    # 其他配置
    http_proxy: Optional[str] = None
    user_agent: Optional[str] = None
    
    # 时间戳
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    last_run_at: Optional[datetime] = None
    
    # 状态
    is_active: bool = True
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            'id': self.id,
            'name': self.name,
            'base_url': self.base_url,
            'cron_expression': self.cron_expression,
            'preset_template': self.preset_template,
            'auth_type': self.auth_type,
            'cookie_string': self.cookie_string,
            'username': self.username,
            'password': '******' if self.password else None,
            'selectors': self.selectors,
            'enable_signin': self.enable_signin,
            'enable_reply': self.enable_reply,
            'enable_feedback': self.enable_feedback,
            'max_daily_replies': self.max_daily_replies,
            'reply_interval_min': self.reply_interval_min,
            'reply_interval_max': self.reply_interval_max,
            'min_reply_count': self.min_reply_count,
            'max_reply_count': self.max_reply_count,
            'reply_randomness': self.reply_randomness,
            'http_proxy': self.http_proxy,
            'user_agent': self.user_agent,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'last_run_at': self.last_run_at.isoformat() if self.last_run_at else None,
            'is_active': self.is_active
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Site':
        """从字典创建"""
        # 处理 selectors 字段
        if 'selectors' in data and isinstance(data['selectors'], str):
            data['selectors'] = json.loads(data['selectors'])
        
        # 处理时间字段
        for field_name in ['created_at', 'updated_at', 'last_run_at']:
            if field_name in data and isinstance(data[field_name], str):
                data[field_name] = datetime.fromisoformat(data[field_name])
        
        return cls(**data)
