"""
浏览器管理器
使用 undetected_chromedriver 绕过反爬虫检测
支持容器环境和本地环境
"""
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
import logging
import time
import os

logger = logging.getLogger(__name__)

class BrowserManager:
    """浏览器管理器类"""
    
    def __init__(self, headless=True, user_agent=None, proxy=None):
        """
        初始化浏览器管理器
        
        Args:
            headless (bool): 是否使用无头模式
            user_agent (str): 自定义 User Agent
            proxy (str): 代理服务器地址
        """
        self.headless = headless
        self.user_agent = user_agent
        self.proxy = proxy
        self.driver = None
        self.is_container = self._detect_container()
        
        logger.info(f'浏览器管理器初始化: headless={headless}, container={self.is_container}')
    
    def _detect_container(self):
        """检测是否在容器环境中运行"""
        # 检查常见的容器标识
        return (
            os.path.exists('/.dockerenv') or
            os.path.exists('/run/.containerenv') or
            os.environ.get('KUBERNETES_SERVICE_HOST') is not None
        )
    
    def get_driver(self):
        """
        获取 Chrome WebDriver 实例
        
        Returns:
            WebDriver: Chrome WebDriver 实例
            
        Raises:
            Exception: 浏览器启动失败时抛出异常
        """
        if self.driver:
            return self.driver
        
        try:
            logger.info('正在配置 Chrome 选项...')
            
            # 创建 ChromeOptions
            options = uc.ChromeOptions()
            
            # ==================== 容器环境必需选项 ====================
            if self.headless:
                # 使用新版无头模式（更稳定）
                options.add_argument('--headless=new')
                logger.info('启用无头模式')
            
            # 容器环境安全选项
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-setuid-sandbox')
            options.add_argument('--disable-gpu')
            
            # ==================== 窗口和显示设置 ====================
            options.add_argument('--window-size=1920,1080')
            options.add_argument('--start-maximized')
            options.add_argument('--disable-blink-features=AutomationControlled')
            
            # ==================== 性能优化 ====================
            options.add_argument('--disable-extensions')
            options.add_argument('--disable-plugins')
            options.add_argument('--disable-images')  # 禁用图片加载以提升速度
            options.add_argument('--disable-javascript')  # 如果不需要 JS，可以禁用
            options.add_argument('--disable-infobars')
            options.add_argument('--disable-notifications')
            options.add_argument('--disable-popup-blocking')
            
            # ==================== 稳定性设置 ====================
            options.add_argument('--ignore-certificate-errors')
            options.add_argument('--ignore-ssl-errors')
            options.add_argument('--disable-web-security')
            options.add_argument('--allow-running-insecure-content')
            options.add_argument('--disable-features=VizDisplayCompositor')
            
            # ==================== 日志控制 ====================
            options.add_argument('--log-level=3')
            options.add_argument('--silent')
            options.add_experimental_option('excludeSwitches', ['enable-automation', 'enable-logging'])
            options.add_experimental_option('useAutomationExtension', False)
            
            # ==================== User Agent 设置 ====================
            if self.user_agent:
                options.add_argument(f'--user-agent={self.user_agent}')
                logger.info(f'使用自定义 User Agent: {self.user_agent[:50]}...')
            else:
                # 默认 User Agent
                default_ua = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
                options.add_argument(f'--user-agent={default_ua}')
            
            # ==================== 代理设置 ====================
            if self.proxy:
                options.add_argument(f'--proxy-server={self.proxy}')
                logger.info(f'使用代理: {self.proxy}')
            
            # ==================== 高级选项 ====================
            prefs = {
                'profile.default_content_setting_values': {
                    'notifications': 2,  # 禁用通知
                    'images': 2,  # 禁用图片
                    'javascript': 1,  # 启用 JavaScript（根据需要调整）
                    'cookies': 1  # 启用 Cookies
                },
                'profile.managed_default_content_settings': {
                    'images': 2
                },
                'download.prompt_for_download': False,
                'download.directory_upgrade': True,
                'safebrowsing.enabled': False,
                'safebrowsing.disable_download_protection': True
            }
            options.add_experimental_option('prefs', prefs)
            
            # ==================== 启动浏览器 ====================
            logger.info('正在启动 Chrome 浏览器...')
            
            # 使用 undetected_chromedriver 创建实例
            self.driver = uc.Chrome(
                options=options,
                version_main=None,  # 自动检测 Chrome 版本
                use_subprocess=True,
                headless=self.headless
            )
            
            logger.info('✅ Chrome WebDriver 启动成功')
            
            # ==================== 浏览器配置 ====================
            # 设置隐式等待（全局）
            self.driver.implicitly_wait(10)
            logger.info('设置隐式等待: 10 秒')
            
            # 设置页面加载超时
            self.driver.set_page_load_timeout(60)
            logger.info('设置页面加载超时: 60 秒')
            
            # 设置脚本执行超时
            self.driver.set_script_timeout(30)
            logger.info('设置脚本执行超时: 30 秒')
            
            # ==================== 反检测脚本 ====================
            try:
                # 注入反检测脚本
                self.driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
                    'source': '''
                        // 隐藏 webdriver 属性
                        Object.defineProperty(navigator, 'webdriver', {
                            get: () => undefined
                        });
                        
                        // 伪造 plugins
                        Object.defineProperty(navigator, 'plugins', {
                            get: () => [1, 2, 3, 4, 5]
                        });
                        
                        // 伪造 languages
                        Object.defineProperty(navigator, 'languages', {
                            get: () => ['zh-CN', 'zh', 'en-US', 'en']
                        });
                        
                        // 伪造 platform
                        Object.defineProperty(navigator, 'platform', {
                            get: () => 'Win32'
                        });
                        
                        // 伪造 hardwareConcurrency
                        Object.defineProperty(navigator, 'hardwareConcurrency', {
                            get: () => 8
                        });
                        
                        // 伪造 deviceMemory
                        Object.defineProperty(navigator, 'deviceMemory', {
                            get: () => 8
                        });
                        
                        // 移除 chrome 对象中的自动化标识
                        if (window.chrome) {
                            delete window.chrome.runtime;
                        }
                        
                        // 覆盖 Permission API
                        const originalQuery = window.navigator.permissions.query;
                        window.navigator.permissions.query = (parameters) => (
                            parameters.name === 'notifications' ?
                                Promise.resolve({ state: Notification.permission }) :
                                originalQuery(parameters)
                        );
                    '''
                })
                logger.info('✅ 反检测脚本注入成功')
            except Exception as e:
                logger.warning(f'反检测脚本注入失败（可忽略）: {e}')
            
            return self.driver
            
        except WebDriverException as e:
            error_msg = f'Chrome WebDriver 启动失败: {str(e)}'
            logger.error(error_msg, exc_info=True)
            
            # 提供更详细的错误提示
            if 'chrome not reachable' in str(e).lower():
                error_msg += '\n提示: Chrome 浏览器可能未正确安装或无法启动'
            elif 'chromedriver' in str(e).lower():
                error_msg += '\n提示: ChromeDriver 版本可能与 Chrome 版本不匹配'
            
            raise Exception(error_msg)
            
        except Exception as e:
            error_msg = f'浏览器启动失败: {str(e)}'
            logger.error(error_msg, exc_info=True)
            raise Exception(error_msg)
    
    def navigate_to(self, url, wait_time=3):
        """
        导航到指定 URL
        
        Args:
            url (str): 目标 URL
            wait_time (int): 页面加载后等待时间（秒）
            
        Returns:
            bool: 导航是否成功
        """
        try:
            logger.info(f'正在导航到: {url}')
            driver = self.get_driver()
            driver.get(url)
            
            # 等待页面加载
            time.sleep(wait_time)
            
            logger.info(f'✅ 成功导航到: {url}')
            return True
            
        except TimeoutException:
            logger.error(f'页面加载超时: {url}')
            return False
        except Exception as e:
            logger.error(f'导航失败: {e}')
            return False
    
    def wait_for_element(self, by, value, timeout=10):
        """
        等待元素出现
        
        Args:
            by: 定位方式（By.ID, By.XPATH 等）
            value: 定位值
            timeout: 超时时间（秒）
            
        Returns:
            WebElement: 找到的元素，未找到返回 None
        """
        try:
            element = WebDriverWait(self.get_driver(), timeout).until(
                EC.presence_of_element_located((by, value))
            )
            logger.info(f'✅ 元素已找到: {value}')
            return element
        except TimeoutException:
            logger.warning(f'元素未找到（超时）: {value}')
            return None
        except Exception as e:
            logger.error(f'等待元素时出错: {e}')
            return None
    
    def get_cookies(self):
        """
        获取当前页面的所有 Cookies
        
        Returns:
            list: Cookie 列表
        """
        try:
            cookies = self.get_driver().get_cookies()
            logger.info(f'获取到 {len(cookies)} 个 Cookies')
            return cookies
        except Exception as e:
            logger.error(f'获取 Cookies 失败: {e}')
            return []
    
    def set_cookies(self, cookies):
        """
        设置 Cookies
        
        Args:
            cookies (list): Cookie 列表
            
        Returns:
            bool: 是否设置成功
        """
        try:
            driver = self.get_driver()
            for cookie in cookies:
                driver.add_cookie(cookie)
            logger.info(f'✅ 成功设置 {len(cookies)} 个 Cookies')
            return True
        except Exception as e:
            logger.error(f'设置 Cookies 失败: {e}')
            return False
    
    def take_screenshot(self, filename=None):
        """
        截取当前页面截图
        
        Args:
            filename (str): 保存文件名，不指定则返回二进制数据
            
        Returns:
            bool/bytes: 保存成功返回 True，否则返回二进制数据或 False
        """
        try:
            driver = self.get_driver()
            
            if filename:
                success = driver.save_screenshot(filename)
                if success:
                    logger.info(f'✅ 截图已保存: {filename}')
                return success
            else:
                screenshot = driver.get_screenshot_as_png()
                logger.info('✅ 截图已生成（二进制数据）')
                return screenshot
                
        except Exception as e:
            logger.error(f'截图失败: {e}')
            return False
    
    def quit(self):
        """关闭浏览器并清理资源"""
        if self.driver:
            try:
                logger.info('正在关闭浏览器...')
                self.driver.quit()
                logger.info('✅ 浏览器已关闭')
            except Exception as e:
                logger.error(f'关闭浏览器失败: {e}')
            finally:
                self.driver = None
    
    def restart(self):
        """重启浏览器"""
        logger.info('正在重启浏览器...')
        self.quit()
        time.sleep(2)
        return self.get_driver()
    
    def __enter__(self):
        """上下文管理器入口"""
        return self.get_driver()
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.quit()
        return False
    
    def __del__(self):
        """析构函数，确保资源被释放"""
        self.quit()


# 便捷函数
def create_browser(headless=True, user_agent=None, proxy=None):
    """
    创建浏览器管理器实例（便捷函数）
    
    Args:
        headless (bool): 是否使用无头模式
        user_agent (str): 自定义 User Agent
        proxy (str): 代理服务器地址
        
    Returns:
        BrowserManager: 浏览器管理器实例
    """
    return BrowserManager(headless=headless, user_agent=user_agent, proxy=proxy)
