"""
站点服务
"""
from typing import List, Optional
import json

# 修复导入路径
from backend.database.db import get_db
from backend.models.site import Site

class SiteService:
    @staticmethod
    def get_all_active_sites() -> List[Site]:
        """获取所有活跃站点"""
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM sites WHERE is_active = 1')
            rows = cursor.fetchall()
            
            sites = []
            for row in rows:
                site_dict = dict(row)
                if site_dict.get('selectors'):
                    site_dict['selectors'] = json.loads(site_dict['selectors'])
                sites.append(Site.from_dict(site_dict))
            
            return sites
    
    @staticmethod
    def get_site_by_id(site_id: int) -> Optional[Site]:
        """根据ID获取站点"""
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM sites WHERE id = ?', (site_id,))
            row = cursor.fetchone()
            
            if not row:
                return None
            
            site_dict = dict(row)
            if site_dict.get('selectors'):
                site_dict['selectors'] = json.loads(site_dict['selectors'])
            
            return Site.from_dict(site_dict)
