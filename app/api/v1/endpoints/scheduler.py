from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from app.core.scheduler import SchedulerService
from app.schemas.response import BaseResponse
import logging

router = APIRouter()
logger = logging.getLogger("fastapi")

class JobInfo(BaseModel):
    id: str
    name: str  # Function name
    title: str # User friendly title
    description: str # Description
    next_run_time: Optional[str] = None
    trigger: str
    is_running: bool = False

@router.get("/jobs", response_model=BaseResponse[List[JobInfo]], summary="获取所有定时任务")
async def get_jobs():
    """
    获取当前调度器中的所有任务列表。
    """
    try:
        jobs = SchedulerService.get_jobs()
        job_list = []
        for job in jobs:
            meta = SchedulerService.get_job_metadata(job.id)
            job_list.append({
                "id": job.id,
                "name": job.name,
                "title": meta.get("title", job.id),
                "description": meta.get("description", ""),
                "next_run_time": job.next_run_time.strftime('%Y-%m-%d %H:%M:%S') if job.next_run_time else None,
                "trigger": str(job.trigger),
                "is_running": SchedulerService.is_job_running(job.id)
            })
        return BaseResponse.success(data=job_list)
    except Exception as e:
        logger.error(f"Error getting jobs: {e}")
        return BaseResponse.fail(code="500", message=str(e))

@router.get("/jobs/{job_id}", response_model=BaseResponse[JobInfo], summary="获取任务详情")
async def get_job(job_id: str):
    """
    获取指定ID的任务详情。
    """
    try:
        job = SchedulerService.get_job(job_id)
        if not job:
            return BaseResponse.fail(code="404", message=f"Job {job_id} not found")
        
        meta = SchedulerService.get_job_metadata(job.id)
        return BaseResponse.success(data={
            "id": job.id,
            "name": job.name,
            "title": meta.get("title", job.id),
            "description": meta.get("description", ""),
            "next_run_time": job.next_run_time.strftime('%Y-%m-%d %H:%M:%S') if job.next_run_time else None,
            "trigger": str(job.trigger),
            "is_running": SchedulerService.is_job_running(job.id)
        })
    except Exception as e:
        logger.error(f"Error getting job {job_id}: {e}")
        return BaseResponse.fail(code="500", message=str(e))

@router.post("/jobs/{job_id}/run", response_model=BaseResponse, summary="立即执行任务")
async def run_job(job_id: str):
    """
    立即触发一次指定任务 (无论计划时间如何)。
    """
    try:
        job = SchedulerService.get_job(job_id)
        if not job:
            return BaseResponse.fail(code="404", message=f"Job {job_id} not found")
            
        SchedulerService.run_job(job_id)
        return BaseResponse.success(message=f"Job {job_id} triggered successfully")
    except Exception as e:
        logger.error(f"Error running job {job_id}: {e}")
        return BaseResponse.fail(code="500", message=str(e))

@router.post("/jobs/{job_id}/pause", response_model=BaseResponse, summary="暂停任务")
async def pause_job(job_id: str):
    """
    暂停指定任务。
    """
    try:
        job = SchedulerService.get_job(job_id)
        if not job:
            return BaseResponse.fail(code="404", message=f"Job {job_id} not found")
            
        SchedulerService.pause_job(job_id)
        return BaseResponse.success(message=f"Job {job_id} paused")
    except Exception as e:
        logger.error(f"Error pausing job {job_id}: {e}")
        return BaseResponse.fail(code="500", message=str(e))

@router.post("/jobs/{job_id}/resume", response_model=BaseResponse, summary="恢复任务")
async def resume_job(job_id: str):
    """
    恢复被暂停的任务。
    """
    try:
        job = SchedulerService.get_job(job_id)
        if not job:
            return BaseResponse.fail(code="404", message=f"Job {job_id} not found")
            
        SchedulerService.resume_job(job_id)
        return BaseResponse.success(message=f"Job {job_id} resumed")
    except Exception as e:
        logger.error(f"Error resuming job {job_id}: {e}")
        return BaseResponse.fail(code="500", message=str(e))

from app.core.database import DBManager

class JobLog(BaseModel):
    id: int
    job_id: str
    job_name: str
    status: str
    start_time: str
    end_time: Optional[str] = None
    duration_seconds: float = 0
    message: str = ""
    created_at: str

@router.get("/logs", response_model=BaseResponse[List[JobLog]], summary="获取任务执行日志")
async def get_logs(limit: int = 50):
    """
    获取最近的任务执行日志。
    """
    try:
        logs = DBManager.get_job_logs(limit)
        log_list = []
        for log in logs:
            log_list.append({
                "id": log["id"],
                "job_id": log["job_id"],
                "job_name": log["job_name"] if log["job_name"] else log["job_id"],
                "status": log["status"],
                "start_time": str(log["start_time"]),
                "end_time": str(log["end_time"]) if log["end_time"] else None,
                "duration_seconds": log["duration_seconds"] if log["duration_seconds"] else 0,
                "message": log["message"] if log["message"] else "",
                "created_at": str(log["create_time"])
            })
        return BaseResponse.success(data=log_list)
    except Exception as e:
        logger.error(f"Error getting logs: {e}")
        return BaseResponse.fail(code="500", message=str(e))
