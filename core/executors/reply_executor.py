"""
回复执行器
"""
from typing import Dict, Tuple, List, Optional
import time
import random
import logging
from selenium.webdriver.common.by import By

# 修复导入路径
from core.browser.browser_manager import BrowserManager
from core.browser.cookie_manager import CookieManager
from core.ai.reply_generator import ReplyGenerator
from core.ai.content_analyzer import ContentAnalyzer
from core.parsers.post_parser import PostParser
from backend.models.site import Site

logger = logging.getLogger(__name__)

class ReplyExecutor:
    def __init__(self, site: Site, ai_generator: ReplyGenerator):
        self.site = site
        self.ai_generator = ai_generator
        self.browser = None
    
    def execute(self) -> Tuple[bool, str, Dict]:
        """
        执行回复任务
        返回: (是否成功, 消息, 详细信息)
        """
        details = {
            'posts_found': 0,
            'posts_replied': 0,
            'posts_skipped': 0,
            'replies': []
        }
        
        try:
            # 初始化浏览器
            self.browser = BrowserManager(
                headless=True,
                user_agent=self.site.user_agent,
                proxy=self.site.http_proxy
            )
            
            # 导航到站点
            self.browser.navigate_to(self.site.base_url)
            time.sleep(2)
            
            # 登录
            if self.site.auth_type == 'cookie' and self.site.cookie_string:
                success = self._login_with_cookie()
            elif self.site.auth_type == 'password' and self.site.username and self.site.password:
                success = self._login_with_password()
            else:
                return False, "未配置有效的登录方式", details
            
            if not success:
                return False, "登录失败", details
            
            # 获取帖子列表
            posts = self._fetch_posts()
            details['posts_found'] = len(posts)
            
            if not posts:
                return True, "未找到可回复的帖子", details
            
            # 回复帖子
            replied_count = 0
            for post in posts[:self.site.max_daily_replies]:
                if self._reply_to_post(post):
                    replied_count += 1
                    details['posts_replied'] += 1
                    details['replies'].append({
                        'post_id': post['id'],
                        'post_title': post['title'],
                        'success': True
                    })
                    
                    # 随机等待
                    wait_time = random.randint(self.site.reply_interval_min, self.site.reply_interval_max)
                    logger.info(f"等待 {wait_time} 秒后继续...")
                    time.sleep(wait_time)
                else:
                    details['posts_skipped'] += 1
                
                if replied_count >= self.site.max_daily_replies:
                    break
            
            message = f"回复完成，成功回复 {replied_count} 个帖子"
            logger.info(message)
            return True, message, details
            
        except Exception as e:
            logger.error(f"回复执行失败: {e}")
            return False, f"回复执行异常: {str(e)}", details
        
        finally:
            if self.browser:
                self.browser.quit()
    
    def _login_with_cookie(self) -> bool:
        """使用Cookie登录"""
        try:
            cookies = CookieManager.parse_cookie_string(self.site.cookie_string)
            if not cookies:
                return False
            
            from urllib.parse import urlparse
            parsed_url = urlparse(self.site.base_url)
            domain = parsed_url.netloc
            
            CookieManager.load_cookies_to_driver(self.browser.driver, cookies, domain)
            return True
        except Exception as e:
            logger.error(f"Cookie登录失败: {e}")
            return False
    
    def _login_with_password(self) -> bool:
        """使用账号密码登录"""
        try:
            login_modal_selector = self.site.selectors.get('login_modal')
            if login_modal_selector:
                ele = self.browser.wait_for_element(By.CSS_SELECTOR, login_modal_selector)
                if ele: ele.click()
                time.sleep(1)
            
            username_selector = self.site.selectors.get('username_input')
            if username_selector:
                ele = self.browser.wait_for_element(By.CSS_SELECTOR, username_selector)
                if ele: ele.send_keys(self.site.username)
            
            password_selector = self.site.selectors.get('password_input')
            if password_selector:
                ele = self.browser.wait_for_element(By.CSS_SELECTOR, password_selector)
                if ele: ele.send_keys(self.site.password)
            
            login_submit_selector = self.site.selectors.get('login_submit')
            if login_submit_selector:
                ele = self.browser.wait_for_element(By.CSS_SELECTOR, login_submit_selector)
                if ele: ele.click()
                time.sleep(3)
            
            return True
        except Exception as e:
            logger.error(f"账号密码登录失败: {e}")
            return False
    
    def _fetch_posts(self) -> List[Dict]:
        """获取帖子列表"""
        try:
            # 导航到帖子列表页
            post_list_url = self.site.selectors.get('post_list_url', '/all')
            if not post_list_url.startswith('http'):
                post_list_url = self.site.base_url.rstrip('/') + '/' + post_list_url.lstrip('/')
            
            self.browser.navigate_to(post_list_url)
            time.sleep(3)
            
            # 获取页面HTML
            html = self.browser.driver.page_source
            
            # 解析帖子列表
            posts = PostParser.parse_post_list(html, self.site.selectors, self.site.base_url)
            
            logger.info(f"获取到 {len(posts)} 个帖子")
            return posts
            
        except Exception as e:
            logger.error(f"获取帖子列表失败: {e}")
            return []
    
    def _reply_to_post(self, post: Dict) -> bool:
        """回复单个帖子"""
        try:
            logger.info(f"准备回复帖子: {post['title']}")
            
            # 导航到帖子详情页
            self.browser.navigate_to(post['link'])
            time.sleep(2)
            
            # 获取帖子内容
            html = self.browser.driver.page_source
            post_detail = PostParser.parse_post_detail(html, self.site.selectors)
            
            # 分析是否应该回复
            should_skip, reason = ContentAnalyzer.should_skip(
                post_detail.get('title', post['title']),
                post_detail.get('content', '')
            )
            
            if should_skip:
                logger.info(f"跳过帖子: {reason}")
                return False
            
            # 生成AI回复
            reply_content = self.ai_generator.generate_reply(
                post_detail.get('title', post['title']),
                post_detail.get('content', ''),
                self.site.min_reply_count,
                self.site.max_reply_count
            )
            
            if not reply_content:
                logger.warning("AI回复生成失败")
                return False
            
            # 执行回复操作
            return self._post_reply(reply_content)
            
        except Exception as e:
            logger.error(f"回复帖子失败: {e}")
            return False
    
    def _post_reply(self, content: str) -> bool:
        """发送回复"""
        try:
            # 点击回复按钮（如果需要）
            reply_dropdown_selector = self.site.selectors.get('reply_dropdown')
            if reply_dropdown_selector:
                ele = self.browser.wait_for_element(By.CSS_SELECTOR, reply_dropdown_selector)
                if ele: 
                    ele.click()
                    time.sleep(1)
            
            # 输入回复内容
            textarea_selector = self.site.selectors.get('reply_textarea')
            if not textarea_selector:
                logger.error("未配置回复输入框选择器")
                return False
            
            ele = self.browser.wait_for_element(By.CSS_SELECTOR, textarea_selector)
            if ele:
                ele.send_keys(content)
                time.sleep(1)
            else:
                return False
            
            # 点击提交按钮
            submit_selector = self.site.selectors.get('reply_submit')
            if not submit_selector:
                logger.error("未配置提交按钮选择器")
                return False
            
            ele = self.browser.wait_for_element(By.CSS_SELECTOR, submit_selector)
            if ele:
                ele.click()
                time.sleep(2)
            else:
                return False
            
            logger.info(f"回复已发送: {content}")
            return True
            
        except Exception as e:
            logger.error(f"发送回复失败: {e}")
            return False
