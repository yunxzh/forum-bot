"""
认证服务
"""
from typing import Optional, Tuple
from datetime import datetime

from database.db import get_db
from models.user import User

class AuthService:
    @staticmethod
    def authenticate(username: str, password: str) -> Tuple[bool, Optional[User], str]:
        """
        认证用户
        返回: (是否成功, 用户对象, 错误消息)
        """
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
            row = cursor.fetchone()
            
            if not row:
                return False, None, '用户名或密码错误'
            
            user = User(
                id=row['id'],
                username=row['username'],
                password_hash=row['password_hash'],
                created_at=datetime.fromisoformat(row['created_at']) if row['created_at'] else None
            )
            
            if not user.verify_password(password):
                return False, None, '用户名或密码错误'
            
            return True, user, ''
    
    @staticmethod
    def update_last_login(user_id: int):
        """更新最后登录时间"""
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute('UPDATE users SET last_login = ? WHERE id = ?', (datetime.now(), user_id))
            conn.commit()
