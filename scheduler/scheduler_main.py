"""
调度器主程序
使用APScheduler进行任务调度
"""
import sys
import os
import logging

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime

from backend.database.db import init_db, get_db
from backend.services.site_service import SiteService
from scheduler.task_runner import TaskRunner

# 确保日志目录存在
log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'logs')
os.makedirs(log_dir, exist_ok=True)

# 获取环境变量中的日志级别，默认为 INFO
log_level_str = os.getenv('LOG_LEVEL', 'INFO').upper()
log_level = getattr(logging, log_level_str, logging.INFO)

# 配置日志
logging.basicConfig(
    level=log_level,  # <--- 修改点：使用动态变量，而不是写死 INFO
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(os.path.join(log_dir, 'scheduler.log'), encoding='utf-8')
    ]
)

# 降低某些啰嗦库的日志级别，否则 DEBUG 模式下会被淹没
logging.getLogger('apscheduler').setLevel(logging.WARNING)
logging.getLogger('urllib3').setLevel(logging.INFO)
logging.getLogger('selenium').setLevel(logging.INFO)

logger = logging.getLogger(__name__)

class ForumBotScheduler:
    def __init__(self):
        self.scheduler = BlockingScheduler()
        self.task_runner = None
        self.jobs = {}
    
    def initialize(self):
        """初始化调度器"""
        logger.info(f"初始化Forum-Bot调度器 (日志级别: {log_level_str})...")
        
        try:
            # 初始化数据库
            db_path = os.getenv('DATABASE_PATH', '/app/data/forum_bot.db')
            
            logger.info(f"正在初始化数据库: {db_path}")
            
            if not os.path.exists(db_path):
                logger.error(f"数据库文件不存在: {db_path}")
                # 注意：这里我们尝试继续，因为如果是首次启动，可能依赖外部初始化
                # 但在该逻辑中通常假定数据库已由 entrypoint 初始化
            
            init_db(db_path)
            logger.info(f"✅ 数据库连接就绪")
            
            self.task_runner = TaskRunner()
            logger.info("✅ TaskRunner 初始化成功")
            
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
    
    def add_site_job(self, site):
        """添加站点任务"""
        try:
            job_id = f"site_{site.id}"
            cron_parts = site.cron_expression.split()
            
            if len(cron_parts) != 5:
                logger.error(f"站点 {site.name} 的Cron表达式格式错误: {site.cron_expression}")
                return
            
            minute, hour, day, month, day_of_week = cron_parts
            
            trigger = CronTrigger(
                minute=minute,
                hour=hour,
                day=day,
                month=month,
                day_of_week=day_of_week
            )
            
            job = self.scheduler.add_job(
                func=self.execute_site_task,
                trigger=trigger,
                args=[site.id],
                id=job_id,
                name=f"{site.name} 定时任务",
                replace_existing=True
            )
            
            self.jobs[site.id] = job
            logger.debug(f"已添加任务调度: {site.name} -> {site.cron_expression}")
            
        except Exception as e:
            logger.error(f"添加站点任务失败 {site.name}: {e}")
    
    def execute_site_task(self, site_id: int):
        """执行站点任务"""
        logger.info(f"开始执行定时任务: site_id={site_id}")
        
        try:
            site = SiteService.get_site_by_id(site_id)
            if not site:
                logger.error(f"站点不存在: {site_id}")
                return
            
            if not site.is_active:
                logger.info(f"站点已禁用，跳过执行: {site.name}")
                return
            
            result = self.task_runner.run_site_tasks(site)
            self.task_runner.send_task_report([result])
            
            logger.info(f"定时任务执行完成: {site.name}")
            
        except Exception as e:
            logger.error(f"执行定时任务失败: {e}", exc_info=True)
    
    def execute_all_sites(self):
        """立即执行所有站点任务"""
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
            
            if results:
                self.task_runner.send_task_report(results)
            logger.info("所有站点任务执行完成")
        except Exception as e:
            logger.error(f"执行所有站点任务失败: {e}", exc_info=True)
    
    def start(self):
        """启动调度器"""
        try:
            logger.info("启动Forum-Bot调度器...")
            self.scheduler.start()
        except (KeyboardInterrupt, SystemExit):
            logger.info("调度器已停止")
        except Exception as e:
            logger.error(f"调度器启动失败: {e}", exc_info=True)
            raise

def main():
    import argparse
    parser = argparse.ArgumentParser(description='Forum-Bot 任务调度器')
    parser.add_argument('--run-once', action='store_true', help='立即执行一次所有任务后退出')
    parser.add_argument('--site-id', type=int, help='只执行指定站点的任务')
    args = parser.parse_args()
    
    try:
        scheduler = ForumBotScheduler()
        scheduler.initialize()
        
        if args.run_once:
            logger.info("运行模式: 单次执行")
            if args.site_id:
                site = SiteService.get_site_by_id(args.site_id)
                if site:
                    result = scheduler.task_runner.run_site_tasks(site)
                    scheduler.task_runner.send_task_report([result])
            else:
                scheduler.execute_all_sites()
        else:
            logger.info("运行模式: 定时调度")
            scheduler.start()
            
    except Exception as e:
        logger.error(f"调度器运行失败: {e}", exc_info=True)
        sys.exit(1)

if __name__ == '__main__':
    main()
