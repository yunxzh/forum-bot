"""
调度器主程序
使用APScheduler进行任务调度
"""
import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime
import logging

from backend.database.db import init_db, get_db
from backend.services.site_service import SiteService
from scheduler.task_runner import TaskRunner

# 确保日志目录存在
log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'logs')
os.makedirs(log_dir, exist_ok=True)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(os.path.join(log_dir, 'scheduler.log'), encoding='utf-8')
    ]
)

logger = logging.getLogger(__name__)

class ForumBotScheduler:
    def __init__(self):
        self.scheduler = BlockingScheduler()
        self.task_runner = None  # ⭐ 延迟初始化
        self.jobs = {}
    
    def initialize(self):
        """初始化调度器"""
        logger.info("初始化Forum-Bot调度器...")
        
        try:
            # ⭐⭐⭐ 关键修复：初始化数据库 ⭐⭐⭐
            db_path = os.getenv('DATABASE_PATH', '/app/data/forum_bot.db')
            
            logger.info(f"正在初始化数据库: {db_path}")
            
            # 检查数据库是否存在
            if not os.path.exists(db_path):
                logger.error(f"数据库文件不存在: {db_path}")
                raise FileNotFoundError(f"数据库文件不存在: {db_path}")
            
            # 初始化数据库连接（设置全局 _db_path）
            init_db(db_path)
            logger.info(f"✅ 数据库初始化成功: {db_path}")
            
            # ⭐ 现在初始化 TaskRunner（需要数据库已初始化）
            self.task_runner = TaskRunner()
            logger.info("✅ TaskRunner 初始化成功")
            
            # 加载所有站点的定时任务
            self.load_site_jobs()
            
            logger.info("调度器初始化完成")
            
        except Exception as e:
            logger.error(f"调度器初始化失败: {e}", exc_info=True)
            raise
    
    def load_site_jobs(self):
        """加载所有站点的定时任务"""
        try:
            sites = SiteService.get_all_active_sites()
            
            logger.info(f"发现 {len(sites)} 个活跃站点")
            
            for site in sites:
                try:
                    self.add_site_job(site)
                except Exception as e:
                    logger.error(f"添加站点任务失败 {site.name}: {e}")
            
            logger.info(f"已加载 {len(self.jobs)} 个定时任务")
            
        except Exception as e:
            logger.error(f"加载站点任务失败: {e}", exc_info=True)
            # 不抛出异常，允许调度器继续运行（即使没有任务）
    
    def add_site_job(self, site):
        """添加站点任务"""
        try:
            job_id = f"site_{site.id}"
            
            # 解析Cron表达式
            cron_parts = site.cron_expression.split()
            
            if len(cron_parts) != 5:
                logger.error(f"站点 {site.name} 的Cron表达式格式错误: {site.cron_expression}")
                return
            
            minute, hour, day, month, day_of_week = cron_parts
            
            # 创建Cron触发器
            trigger = CronTrigger(
                minute=minute,
                hour=hour,
                day=day,
                month=month,
                day_of_week=day_of_week
            )
            
            # 添加任务
            job = self.scheduler.add_job(
                func=self.execute_site_task,
                trigger=trigger,
                args=[site.id],
                id=job_id,
                name=f"{site.name} 定时任务",
                replace_existing=True
            )
            
            self.jobs[site.id] = job
            
            logger.info(f"已添加定时任务: {site.name} ({site.cron_expression})")
            
        except Exception as e:
            logger.error(f"添加站点任务失败 {site.name}: {e}")
    
    def execute_site_task(self, site_id: int):
        """执行站点任务"""
        logger.info(f"开始执行定时任务: site_id={site_id}")
        
        try:
            # 获取站点信息
            site = SiteService.get_site_by_id(site_id)
            
            if not site:
                logger.error(f"站点不存在: {site_id}")
                return
            
            if not site.is_active:
                logger.info(f"站点已禁用，跳过执行: {site.name}")
                return
            
            # 执行任务
            result = self.task_runner.run_site_tasks(site)
            
            # 发送通知
            self.task_runner.send_task_report([result])
            
            logger.info(f"定时任务执行完成: {site.name}")
            
        except Exception as e:
            logger.error(f"执行定时任务失败: {e}", exc_info=True)
    
    def execute_all_sites(self):
        """立即执行所有站点任务（用于测试）"""
        logger.info("开始执行所有站点任务...")
        
        try:
            sites = SiteService.get_all_active_sites()
            results = []
            
            for site in sites:
                try:
                    result = self.task_runner.run_site_tasks(site)
                    results.append(result)
                except Exception as e:
                    logger.error(f"执行站点任务失败 {site.name}: {e}")
            
            # 发送汇总报告
            if results:
                self.task_runner.send_task_report(results)
            
            logger.info("所有站点任务执行完成")
            
        except Exception as e:
            logger.error(f"执行所有站点任务失败: {e}", exc_info=True)
    
    def start(self):
        """启动调度器"""
        try:
            logger.info("启动Forum-Bot调度器...")
            logger.info(f"当前已加载 {len(self.jobs)} 个定时任务")
            
            # 显示所有任务
            jobs = self.scheduler.get_jobs()
            if jobs:
                logger.info("已配置的定时任务:")
                for job in jobs:
                    logger.info(f"  - {job.name}: {job.trigger}")
            else:
                logger.warning("没有配置任何定时任务，调度器将处于待机状态")
            
            # 启动调度器
            self.scheduler.start()
            
        except (KeyboardInterrupt, SystemExit):
            logger.info("调度器已停止")
        except Exception as e:
            logger.error(f"调度器启动失败: {e}", exc_info=True)
            raise
    
    def reload_jobs(self):
        """重新加载所有任务（用于配置更新后）"""
        logger.info("重新加载定时任务...")
        
        # 移除所有现有任务
        for job_id in list(self.jobs.keys()):
            try:
                self.scheduler.remove_job(job_id)
                del self.jobs[job_id]
            except Exception as e:
                logger.error(f"移除任务失败 {job_id}: {e}")
        
        # 重新加载
        self.load_site_jobs()
        
        logger.info("任务重新加载完成")

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Forum-Bot 任务调度器')
    parser.add_argument('--run-once', action='store_true', help='立即执行一次所有任务后退出')
    parser.add_argument('--site-id', type=int, help='只执行指定站点的任务')
    
    args = parser.parse_args()
    
    try:
        logger.info("="*50)
        logger.info("Forum-Bot Scheduler Starting...")
        logger.info("="*50)
        
        scheduler = ForumBotScheduler()
        scheduler.initialize()
        
        if args.run_once:
            # 单次运行模式
            logger.info("运行模式: 单次执行")
            if args.site_id:
                site = SiteService.get_site_by_id(args.site_id)
                if site:
                    result = scheduler.task_runner.run_site_tasks(site)
                    scheduler.task_runner.send_task_report([result])
                else:
                    logger.error(f"站点不存在: {args.site_id}")
            else:
                scheduler.execute_all_sites()
        else:
            # 调度模式
            logger.info("运行模式: 定时调度")
            scheduler.start()
            
    except Exception as e:
        logger.error(f"调度器运行失败: {e}", exc_info=True)
        sys.exit(1)

if __name__ == '__main__':
    main()
