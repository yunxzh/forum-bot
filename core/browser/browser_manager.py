"""
浏览器管理模块
基于 undetected-chromedriver
"""
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
import os
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

class BrowserManager:
    def __init__(self, headless: bool = False, user_agent: Optional[str] = None, proxy: Optional[str] = None):
        self.headless = headless
        self.user_agent = user_agent
        self.proxy = proxy
        self.driver: Optional[uc.Chrome] = None
    
    def start(self) -> uc.Chrome:
        """启动浏览器"""
        options = uc.ChromeOptions()
        
        if self.headless:
            options.add_argument('--headless=new')
        
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-blink-features=AutomationControlled')
        
        if self.user_agent:
            options.add_argument(f'user-agent={self.user_agent}')
        
        if self.proxy:
            options.add_argument(f'--proxy-server={self.proxy}')
        
        # 检查是否在Docker中运行
        if os.getenv('IN_DOCKER', 'false').lower() == 'true':
            options.binary_location = '/usr/bin/chromium'
            driver_executable_path = '/usr/bin/chromedriver'
        else:
            driver_executable_path = None
        
        # 获取Chrome版本
        chrome_version = os.getenv('CHROME_VERSION', '')
        version_main = int(chrome_version) if chrome_version.isdigit() else None
        
        try:
            self.driver = uc.Chrome(
                options=options,
                driver_executable_path=driver_executable_path,
                version_main=version_main
            )
            logger.info("浏览器启动成功")
            return self.driver
        except Exception as e:
            logger.error(f"浏览器启动失败: {e}")
            raise
    
    def quit(self):
        """关闭浏览器"""
        if self.driver:
            try:
                self.driver.quit()
                logger.info("浏览器已关闭")
            except Exception as e:
                logger.error(f"关闭浏览器失败: {e}")
            finally:
                self.driver = None
    
    def navigate(self, url: str, wait_time: int = 10):
        """导航到指定URL"""
        if not self.driver:
            raise RuntimeError("浏览器未启动")
        
        logger.info(f"导航到: {url}")
        self.driver.get(url)
        time.sleep(wait_time)
    
    def find_element(self, selector: str, by: By = By.CSS_SELECTOR, timeout: int = 10):
        """查找元素"""
        if not self.driver:
            raise RuntimeError("浏览器未启动")
        
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((by, selector))
            )
            return element
        except TimeoutException:
            logger.warning(f"未找到元素: {selector}")
            return None
    
    def find_elements(self, selector: str, by: By = By.CSS_SELECTOR):
        """查找多个元素"""
        if not self.driver:
            raise RuntimeError("浏览器未启动")
        
        try:
            return self.driver.find_elements(by, selector)
        except NoSuchElementException:
            return []
    
    def click(self, selector: str, by: By = By.CSS_SELECTOR, timeout: int = 10) -> bool:
        """点击元素"""
        element = self.find_element(selector, by, timeout)
        if element:
            try:
                element.click()
                logger.info(f"点击元素: {selector}")
                return True
            except Exception as e:
                logger.error(f"点击元素失败 {selector}: {e}")
                return False
        return False
    
    def input_text(self, selector: str, text: str, by: By = By.CSS_SELECTOR, timeout: int = 10) -> bool:
        """输入文本"""
        element = self.find_element(selector, by, timeout)
        if element:
            try:
                element.clear()
                element.send_keys(text)
                logger.info(f"输入文本到 {selector}")
                return True
            except Exception as e:
                logger.error(f"输入文本失败 {selector}: {e}")
                return False
        return False
    
    def get_text(self, selector: str, by: By = By.CSS_SELECTOR, timeout: int = 10) -> Optional[str]:
        """获取元素文本"""
        element = self.find_element(selector, by, timeout)
        if element:
            return element.text
        return None
    
    def get_attribute(self, selector: str, attribute: str, by: By = By.CSS_SELECTOR, timeout: int = 10) -> Optional[str]:
        """获取元素属性"""
        element = self.find_element(selector, by, timeout)
        if element:
            return element.get_attribute(attribute)
        return None
    
    def execute_script(self, script: str, *args):
        """执行JavaScript"""
        if not self.driver:
            raise RuntimeError("浏览器未启动")
        
        return self.driver.execute_script(script, *args)
    
    def wait_for_element(self, selector: str, by: By = By.CSS_SELECTOR, timeout: int = 10) -> bool:
        """等待元素出现"""
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((by, selector))
            )
            return True
        except TimeoutException:
            return False
    
    def screenshot(self, filename: str):
        """截图"""
        if self.driver:
            self.driver.save_screenshot(filename)
            logger.info(f"截图已保存: {filename}")
