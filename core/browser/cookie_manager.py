"""
Cookie管理模块
"""
import json
import pickle
from pathlib import Path
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class CookieManager:
    @staticmethod
    def parse_cookie_string(cookie_string: str) -> List[Dict[str, Any]]:
        """
        解析Cookie字符串为Cookie列表
        支持两种格式:
        1. 浏览器导出格式: name1=value1; name2=value2
        2. JSON格式: [{"name": "xxx", "value": "xxx"}]
        """
        if not cookie_string or not cookie_string.strip():
            return []
        
        cookie_string = cookie_string.strip()
        
        # 尝试解析JSON格式
        if cookie_string.startswith('['):
            try:
                return json.loads(cookie_string)
            except json.JSONDecodeError:
                logger.warning("JSON格式Cookie解析失败，尝试解析为键值对格式")
        
        # 解析键值对格式
        cookies = []
        for cookie_pair in cookie_string.split(';'):
            cookie_pair = cookie_pair.strip()
            if '=' in cookie_pair:
                name, value = cookie_pair.split('=', 1)
                cookies.append({
                    'name': name.strip(),
                    'value': value.strip()
                })
        
        return cookies
    
    @staticmethod
    def load_cookies_to_driver(driver, cookies: List[Dict[str, Any]], domain: Optional[str] = None):
        """
        将Cookie加载到浏览器
        """
        for cookie in cookies:
            cookie_dict = {
                'name': cookie.get('name'),
                'value': cookie.get('value')
            }
            
            # 添加可选字段
            if cookie.get('domain'):
                cookie_dict['domain'] = cookie['domain']
            elif domain:
                cookie_dict['domain'] = domain
            
            if cookie.get('path'):
                cookie_dict['path'] = cookie['path']
            else:
                cookie_dict['path'] = '/'
            
            if cookie.get('secure') is not None:
                cookie_dict['secure'] = cookie['secure']
            
            if cookie.get('httpOnly') is not None:
                cookie_dict['httpOnly'] = cookie['httpOnly']
            
            if cookie.get('expiry'):
                cookie_dict['expiry'] = cookie['expiry']
            
            try:
                driver.add_cookie(cookie_dict)
            except Exception as e:
                logger.warning(f"添加Cookie失败 {cookie_dict['name']}: {e}")
    
    @staticmethod
    def save_cookies_from_driver(driver, filepath: str):
        """
        从浏览器保存Cookie到文件
        """
        cookies = driver.get_cookies()
        
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(cookies, f, indent=2)
        
        logger.info(f"Cookie已保存到: {filepath}")
    
    @staticmethod
    def load_cookies_from_file(filepath: str) -> List[Dict[str, Any]]:
        """
        从文件加载Cookie
        """
        if not Path(filepath).exists():
            logger.warning(f"Cookie文件不存在: {filepath}")
            return []
        
        with open(filepath, 'r', encoding='utf-8') as f:
            cookies = json.load(f)
        
        logger.info(f"从文件加载了 {len(cookies)} 个Cookie")
        return cookies
