"""
签到执行器
"""
from typing import Dict, Tuple
import time
import logging

# 修复导入路径
from core.browser.browser_manager import BrowserManager
from core.browser.cookie_manager import CookieManager
from backend.models.site import Site

logger = logging.getLogger(__name__)

class SignInExecutor:
    def __init__(self, site: Site):
        self.site = site
        self.browser = None
    
    def execute(self) -> Tuple[bool, str, Dict]:
        """
        执行签到任务
        返回: (是否成功, 消息, 详细信息)
        """
        details = {}
        
        try:
            # 初始化浏览器
            self.browser = BrowserManager(
                headless=True,
                user_agent=self.site.user_agent,
                proxy=self.site.http_proxy
            )
            
            self.browser.start()
            
            # 导航到站点
            self.browser.navigate(self.site.base_url)
            time.sleep(2)
            
            # 加载Cookie或登录
            if self.site.auth_type == 'cookie' and self.site.cookie_string:
                success = self._login_with_cookie()
            elif self.site.auth_type == 'password' and self.site.username and self.site.password:
                success = self._login_with_password()
            else:
                return False, "未配置有效的登录方式", details
            
            if not success:
                return False, "登录失败", details
            
            # 刷新页面确保Cookie生效
            self.browser.navigate(self.site.base_url)
            time.sleep(2)
            
            # 执行签到
            signin_selector = self.site.selectors.get('signin_button')
            if not signin_selector:
                return False, "未配置签到按钮选择器", details
            
            # 查找签到按钮
            signin_button = self.browser.find_element(signin_selector)
            if not signin_button:
                # 可能已经签到过了
                details['already_signed'] = True
                return True, "今日已签到或未找到签到按钮", details
            
            # 点击签到按钮
            if self.browser.click(signin_selector):
                time.sleep(2)
                
                # 检查是否需要确认
                confirm_selector = self.site.selectors.get('signin_confirm')
                if confirm_selector:
                    self.browser.click(confirm_selector)
                    time.sleep(1)
                
                details['signed'] = True
                logger.info(f"站点 {self.site.name} 签到成功")
                return True, "签到成功", details
            else:
                return False, "点击签到按钮失败", details
            
        except Exception as e:
            logger.error(f"签到执行失败: {e}")
            return False, f"签到执行异常: {str(e)}", details
        
        finally:
            if self.browser:
                self.browser.quit()
    
    def _login_with_cookie(self) -> bool:
        """使用Cookie登录"""
        try:
            cookies = CookieManager.parse_cookie_string(self.site.cookie_string)
            if not cookies:
                logger.error("Cookie解析失败")
                return False
            
            # 提取域名
            from urllib.parse import urlparse
            parsed_url = urlparse(self.site.base_url)
            domain = parsed_url.netloc
            
            CookieManager.load_cookies_to_driver(self.browser.driver, cookies, domain)
            logger.info("Cookie加载成功")
            return True
            
        except Exception as e:
            logger.error(f"Cookie登录失败: {e}")
            return False
    
    def _login_with_password(self) -> bool:
        """使用账号密码登录"""
        try:
            # 点击登录入口
            login_modal_selector = self.site.selectors.get('login_modal')
            if login_modal_selector:
                self.browser.click(login_modal_selector)
                time.sleep(1)
            
            # 输入用户名
            username_selector = self.site.selectors.get('username_input')
            if username_selector:
                self.browser.input_text(username_selector, self.site.username)
            
            # 输入密码
            password_selector = self.site.selectors.get('password_input')
            if password_selector:
                self.browser.input_text(password_selector, self.site.password)
            
            # 点击登录按钮
            login_submit_selector = self.site.selectors.get('login_submit')
            if login_submit_selector:
                self.browser.click(login_submit_selector)
                time.sleep(3)
            
            # 检查是否登录成功（可以根据页面变化判断）
            # 这里简单返回True，实际应该检查登录状态
            logger.info("账号密码登录完成")
            return True
            
        except Exception as e:
            logger.error(f"账号密码登录失败: {e}")
            return False
