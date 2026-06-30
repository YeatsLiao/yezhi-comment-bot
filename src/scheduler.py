"""
定时任务调度器
"""
import logging
import time
import schedule
from datetime import datetime
from typing import Callable, Optional

logger = logging.getLogger(__name__)


class TaskScheduler:
    """定时任务调度器"""
    
    def __init__(self, config: dict):
        self.config = config.get("scheduler", {})
        self.enabled = self.config.get("enabled", False)
        self.hour = self.config.get("hour", 8)
        self.minute = self.config.get("minute", 0)
        self.timezone = self.config.get("timezone", "Asia/Shanghai")
    
    def schedule_task(self, task_func: Callable):
        """注册定时任务"""
        if not self.enabled:
            logger.info("定时调度未启用，将仅执行一次")
            return
        
        # 设置每日定时任务
        schedule_time = f"{self.hour:02d}:{self.minute:02d}"
        schedule.every().day.at(schedule_time).do(task_func)
        logger.info(f"定时任务已注册：每天 {schedule_time} 执行")
    
    def run_pending(self):
        """检查并执行到期的任务"""
        schedule.run_pending()
    
    def run_loop(self, task_func: Callable):
        """运行调度循环"""
        if not self.enabled:
            # 非调度模式，直接执行一次
            logger.info("非调度模式，立即执行一次任务")
            task_func()
            return
        
        # 注册并运行定时任务
        self.schedule_task(task_func)
        logger.info(f"调度器已启动，等待每天 {self.hour:02d}:{self.minute:02d} 执行...")
        
        try:
            while True:
                self.run_pending()
                time.sleep(60)  # 每分钟检查一次
        except KeyboardInterrupt:
            logger.info("调度器已停止")
