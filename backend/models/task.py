"""
任务执行记录模型
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional
import json

@dataclass
class TaskLog:
    id: Optional[int]
    site_id: int
    task_type: str  # 'signin', 'reply', 'feedback'
    status: str  # 'success', 'failed', 'skipped'
    message: Optional[str] = None
    details: Optional[dict] = None
    executed_at: Optional[datetime] = None
    duration: Optional[float] = None  # 执行耗时（秒）
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            'id': self.id,
            'site_id': self.site_id,
            'task_type': self.task_type,
            'status': self.status,
            'message': self.message,
            'details': self.details,
            'executed_at': self.executed_at.isoformat() if self.executed_at else None,
            'duration': self.duration
        }
