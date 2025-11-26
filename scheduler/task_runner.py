"""
任务运行器
执行具体的站点任务
"""
import time
from typing import Dict, Any
import logging

from models.site import Site
from core.executors.signin_executor import SignInExecutor
from core.executors.reply_executor import ReplyExecutor
from core.ai.reply_generator import ReplyGenerator
from services.task_service import TaskService
from services.notification_service import NotificationService
from database.db import get_db

logger = logging.getLogger(__name__)

class TaskRunner:
    def __init__(self):
        self.notification_service = NotificationService()
    
    def run_site_tasks(self, site: Site) -> Dict[str, Any]:
        """
        运行单个站点的所有任务
        返回执行结果
        """
        logger.info(f"开始执行站点任务: {site.name}")
        
        result = {
            'site_id': site.id,
            'site_name': site.name,
            'signin': None,
            'reply': None,
            'success': False,
            'message': ''
        }
        
        start_time = time.time()
        
        try:
            # 执行签到任务
            if site.enable_signin:
                signin_result = self._run_signin(site)
                result['signin'] = signin_result
            
            # 执行回复任务
            if site.enable_reply:
                reply_result = self._run_reply(site)
                result['reply'] = reply_result
            
            # 更新站点最后运行时间
            TaskService.update_site_last_run(site.id)
            
            result['success'] = True
            result['message'] = '任务执行完成'
            
        except Exception as e:
            logger.error(f"执行站点任务失败: {e}", exc_info=True)
            result['success'] = False
            result['message'] = f'任务执行异常: {str(e)}'
        
        finally:
            duration = time.time() - start_time
            result['duration'] = duration
            logger.info(f"站点任务执行完成: {site.name}, 耗时: {duration:.2f}秒")
        
        return result
    
    def _run_signin(self, site: Site) -> Dict[str, Any]:
        """执行签到任务"""
        logger.info(f"执行签到任务: {site.name}")
        start_time = time.time()
        
        executor = SignInExecutor(site)
        success, message, details = executor.execute()
        duration = time.time() - start_time
        
        # 记录任务日志
        TaskService.create_task_log(
            site_id=site.id,
            task_type='signin',
            status='success' if success else 'failed',
            message=message,
            details=details,
            duration=duration
        )
        
        return {
            'success': success,
            'message': message,
            'details': details,
            'duration': duration
        }
    
    def _run_reply(self, site: Site) -> Dict[str, Any]:
        """执行回复任务"""
        logger.info(f"执行回复任务: {site.name}")
        start_time = time.time()
        
        # 获取AI配置
        ai_config = self._get_ai_config()
        if not ai_config:
            return {
                'success': False,
                'message': 'AI配置未设置',
                'details': {},
                'duration': 0
            }
        
        # 创建AI生成器
        ai_generator = ReplyGenerator(
            api_key=ai_config['api_key'],
            base_url=ai_config['base_url'],
            model=ai_config['model'],
            temperature=ai_config.get('temperature', 0.8),
            max_tokens=ai_config.get('max_tokens', 100)
        )
        
        executor = ReplyExecutor(site, ai_generator)
        success, message, details = executor.execute()
        duration = time.time() - start_time
        
        # 记录任务日志
        TaskService.create_task_log(
            site_id=site.id,
            task_type='reply',
            status='success' if success else 'failed',
            message=message,
            details=details,
            duration=duration
        )
        
        return {
            'success': success,
            'message': message,
            'details': details,
            'duration': duration
        }
    
    def _get_ai_config(self) -> Dict[str, Any]:
        """获取AI配置"""
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM ai_config WHERE id = 1')
            row = cursor.fetchone()
            
            if not row:
                return None
            
            return dict(row)
    
    def send_task_report(self, results: list):
        """发送任务报告"""
        if not self.notification_service.is_any_enabled():
            logger.info("未启用任何通知渠道，跳过发送报告")
            return
        
        # 构建报告内容
        title = "Forum-Bot 任务执行报告"
        
        content_lines = ["任务执行完成！\n"]
        
        # 统计信息
        total_sites = len(results)
        success_sites = sum(1 for r in results if r.get('success', False))
        
        content_lines.append(f"📊 总览:")
        content_lines.append(f"  • 站点总数: {total_sites}")
        content_lines.append(f"  • 成功执行: {success_sites}")
        content_lines.append(f"  • 执行失败: {total_sites - success_sites}\n")
        
        # 详细信息
        for result in results:
            site_name = result.get('site_name', 'Unknown')
            success = result.get('success', False)
            
            status_emoji = "✅" if success else "❌"
            content_lines.append(f"{status_emoji} {site_name}")
            
            # 签到结果
            if result.get('signin'):
                signin = result['signin']
                signin_status = "成功" if signin.get('success') else "失败"
                content_lines.append(f"  签到: {signin_status} - {signin.get('message', '')}")
            
            # 回复结果
            if result.get('reply'):
                reply = result['reply']
                reply_status = "成功" if reply.get('success') else "失败"
                details = reply.get('details', {})
                replied = details.get('posts_replied', 0)
                content_lines.append(f"  回复: {reply_status} - 已回复 {replied} 个帖子")
            
            content_lines.append("")
        
        content = "\n".join(content_lines)
        
        # 发送通知
        try:
            self.notification_service.send(title, content)
            logger.info("任务报告已发送")
        except Exception as e:
            logger.error(f"发送任务报告失败: {e}")
