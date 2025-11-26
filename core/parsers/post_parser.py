"""
帖子解析器
从页面中提取帖子信息
"""
from typing import List, Dict, Optional
import re
from bs4 import BeautifulSoup
import logging

logger = logging.getLogger(__name__)

class PostParser:
    @staticmethod
    def parse_post_list(html: str, selectors: Dict[str, str], base_url: str) -> List[Dict[str, str]]:
        """
        解析帖子列表页面
        返回帖子列表
        """
        soup = BeautifulSoup(html, 'html.parser')
        posts = []
        
        post_item_selector = selectors.get('post_item', 'li[data-id]')
        title_selector = selectors.get('post_title', '.DiscussionListItem-title')
        link_selector = selectors.get('post_link', '.DiscussionListItem-main a')
        
        # 查找所有帖子项
        post_elements = soup.select(post_item_selector)
        
        for element in post_elements:
            try:
                # 提取标题
                title_elem = element.select_one(title_selector)
                title = title_elem.get_text(strip=True) if title_elem else ""
                
                # 提取链接
                link_elem = element.select_one(link_selector)
                if link_elem:
                    link = link_elem.get('href', '')
                    if link and not link.startswith('http'):
                        link = base_url.rstrip('/') + '/' + link.lstrip('/')
                else:
                    link = ""
                
                # 提取帖子ID
                post_id = PostParser.extract_post_id(link, element)
                
                if title and link and post_id:
                    posts.append({
                        'id': post_id,
                        'title': title,
                        'link': link
                    })
            
            except Exception as e:
                logger.warning(f"解析帖子项失败: {e}")
                continue
        
        logger.info(f"解析到 {len(posts)} 个帖子")
        return posts
    
    @staticmethod
    def parse_post_detail(html: str, selectors: Dict[str, str]) -> Dict[str, str]:
        """
        解析帖子详情页面
        返回帖子详细信息
        """
        soup = BeautifulSoup(html, 'html.parser')
        
        title_selector = selectors.get('detail_title', '.DiscussionHero-title')
        content_selector = selectors.get('detail_content', '.Post-body')
        
        # 提取标题
        title_elem = soup.select_one(title_selector)
        title = title_elem.get_text(strip=True) if title_elem else ""
        
        # 提取内容
        content_elem = soup.select_one(content_selector)
        content = content_elem.get_text(strip=True) if content_elem else ""
        
        return {
            'title': title,
            'content': content
        }
    
    @staticmethod
    def extract_post_id(link: str, element=None) -> Optional[str]:
        """
        从链接或元素中提取帖子ID
        """
        # 尝试从链接中提取
        if link:
            # 匹配常见的帖子ID模式
            patterns = [
                r'/d/(\d+)',           # Flarum: /d/123
                r'/post-(\d+)',        # NodeLoc: /post-123-1-1.html
                r'/t/[^/]+/(\d+)',     # Discourse: /t/topic-name/123
                r'[?&]tid=(\d+)',      # 传统论坛: ?tid=123
            ]
            
            for pattern in patterns:
                match = re.search(pattern, link)
                if match:
                    return match.group(1)
        
        # 尝试从元素属性中提取
        if element:
            # data-id 属性
            post_id = element.get('data-id')
            if post_id:
                return str(post_id)
            
            # id 属性
            elem_id = element.get('id')
            if elem_id:
                # 尝试提取数字部分
                match = re.search(r'\d+', elem_id)
                if match:
                    return match.group(0)
        
        return None
