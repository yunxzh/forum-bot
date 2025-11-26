"""
任务服务
"""
from typing import Optional
from datetime import datetime
import json

# 修复导入路径
from backend.database.db import get_db
from backend.models.task import TaskLog

class TaskService:
    @staticmethod
    def create_task_log(
        site_id: int,
        task_type: str,
        status: str,
        message: Optional[str] = None,
        details: Optional[dict] = None,
        duration: Optional[float] = None
    ) -> int:
        """创建任务日志"""
        with get_db() as conn:
            cursor = conn.cursor()
            
            details_json = json.dumps(details) if details else None
            
            cursor.execute('''
                INSERT INTO task_logs (
                    site_id, task_type, status, message, details, duration
                ) VALUES (?, ?, ?, ?, ?, ?)
            ''', (site_id, task_type, status, message, details_json, duration))
            
            conn.commit()
            return cursor.lastrowid
    
    @staticmethod
    def update_site_last_run(site_id: int):
        """更新站点最后运行时间"""
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute('UPDATE sites SET last_run_at = ? WHERE id = ?', (datetime.now(), site_id))
            conn.commit()
