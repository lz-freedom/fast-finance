from apscheduler.events import EVENT_JOB_SUBMITTED, EVENT_JOB_EXECUTED, EVENT_JOB_ERROR
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.core.database import DBManager

import logging
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime
from app.services.yahoo_sync_service import YahooSyncService
from app.services.tradingview_sync_service import tradingview_sync_service
from app.services.investing_sync_service import investing_sync_service

logger = logging.getLogger("fastapi")

class SchedulerService:
    _scheduler = None
    _running_logs = {} # job_id -> log_id mapping (simple in-memory tracking)

    @classmethod
    def job_listener(cls, event):
        """
        Listener for job events to log execution history.
        """
        try:
            job_id = event.job_id
            
            if event.code == EVENT_JOB_SUBMITTED:
                # Job started
                meta = cls.get_job_metadata(job_id)
                job_name = meta.get("title", job_id)
                log_id = DBManager.log_job_start(job_id, job_name)
                if log_id > 0:
                    cls._running_logs[job_id] = log_id
                    
            elif event.code == EVENT_JOB_EXECUTED:
                # Job finished successfully
                log_id = cls._running_logs.get(job_id)
                if log_id:
                    DBManager.log_job_finish(log_id, "SUCCESS")
                    # Clean up memory
                    cls._running_logs.pop(job_id, None)
                    
            elif event.code == EVENT_JOB_ERROR:
                # Job failed
                log_id = cls._running_logs.get(job_id)
                if log_id:
                    msg = str(event.exception) if event.exception else "Unknown error"
                    DBManager.log_job_finish(log_id, "FAILED", msg)
                    cls._running_logs.pop(job_id, None)
                    
        except Exception as e:
            logger.error(f"Error in job listener: {e}")

    @classmethod
    def start(cls):
        if cls._scheduler:
            return

        cls._scheduler = AsyncIOScheduler(timezone="Asia/Shanghai")
        cls._scheduler.add_listener(cls.job_listener, EVENT_JOB_SUBMITTED | EVENT_JOB_EXECUTED | EVENT_JOB_ERROR)
        
        # ... (rest of add_job calls) ...

        
        # Yahoo Finance Sync Tasks
        # 07:05
        cls._scheduler.add_job(
            YahooSyncService.sync_all_stocks,
            CronTrigger(hour=7, minute=5, timezone="Asia/Shanghai"),
            id="yahoo_sync_morning",
            replace_existing=True,
            misfire_grace_time=60
        )
        # 19:05
        cls._scheduler.add_job(
            YahooSyncService.sync_all_stocks,
            CronTrigger(hour=19, minute=5, timezone="Asia/Shanghai"),
            id="yahoo_sync_evening",
            replace_existing=True,
            misfire_grace_time=60
        )

        # TradingView Sync Tasks
        # 07:35
        cls._scheduler.add_job(
            tradingview_sync_service.start_sync_task,
            CronTrigger(hour=7, minute=35, timezone="Asia/Shanghai"),
            id="tradingview_sync_morning",
            replace_existing=True,
            misfire_grace_time=60
        )
        # 19:35
        cls._scheduler.add_job(
            tradingview_sync_service.start_sync_task,
            CronTrigger(hour=19, minute=35, timezone="Asia/Shanghai"),
            id="tradingview_sync_evening",
            replace_existing=True,
            misfire_grace_time=60
        )

        # Investing Sync Tasks
        # 08:05
        cls._scheduler.add_job(
            investing_sync_service.start_sync_task,
            CronTrigger(hour=8, minute=5, timezone="Asia/Shanghai"),
            id="investing_sync_morning",
            replace_existing=True,
            misfire_grace_time=60
        )
        # 20:05
        cls._scheduler.add_job(
            investing_sync_service.start_sync_task,
            CronTrigger(hour=20, minute=5, timezone="Asia/Shanghai"),
            id="investing_sync_evening",
            replace_existing=True,
            misfire_grace_time=60
        )

        cls._scheduler.start()
        logger.info("Scheduler Service started. Tasks scheduled: Yahoo(07:05, 19:05), TV(07:35, 19:35), Investing(08:05, 20:05) [Asia/Shanghai]")

    @classmethod
    def stop(cls):
        if cls._scheduler:
            cls._scheduler.shutdown()
            cls._scheduler = None
            logger.info("Scheduler Service stopped.")

    JOB_METADATA = {
        "yahoo_sync_morning": {"title": "Yahoo 早间同步", "description": "全量同步 Yahoo Finance 股票数据 (07:05)"},
        "yahoo_sync_evening": {"title": "Yahoo 晚间同步", "description": "全量同步 Yahoo Finance 股票数据 (19:05)"},
        "tradingview_sync_morning": {"title": "TradingView 早间同步", "description": "同步 TradingView 技术分析数据 (07:35)"},
        "tradingview_sync_evening": {"title": "TradingView 晚间同步", "description": "同步 TradingView 技术分析数据 (19:35)"},
        "investing_sync_morning": {"title": "Investing 早间同步", "description": "同步 Investing.com 数据 (08:05)"},
        "investing_sync_evening": {"title": "Investing 晚间同步", "description": "同步 Investing.com 数据 (20:05)"},
    }

    @classmethod
    def get_job_metadata(cls, job_id: str):
        return cls.JOB_METADATA.get(job_id, {"title": job_id, "description": ""})

    @classmethod
    def get_jobs(cls):
        if not cls._scheduler:
            return []
        return cls._scheduler.get_jobs()

    @classmethod
    def get_job(cls, job_id: str):
        if not cls._scheduler:
            return None
        return cls._scheduler.get_job(job_id)

    @classmethod
    def pause_job(cls, job_id: str):
        if cls._scheduler:
            cls._scheduler.pause_job(job_id)

    @classmethod
    def resume_job(cls, job_id: str):
        if cls._scheduler:
            cls._scheduler.resume_job(job_id)

    @classmethod
    def run_job(cls, job_id: str):
        if cls._scheduler:
            job = cls._scheduler.get_job(job_id)
            if job:
                job.modify(next_run_time=datetime.now(cls._scheduler.timezone))

    @classmethod
    def is_job_running(cls, job_id: str) -> bool:
        return job_id in cls._running_logs

