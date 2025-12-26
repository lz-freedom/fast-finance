from fastapi import APIRouter, BackgroundTasks
from app.schemas.response import BaseResponse
from app.services.yahoo_sync_service import YahooSyncService

router = APIRouter()

@router.post("/task/yahoo_stock_update", response_model=BaseResponse, summary="触发雅虎股票全量更新任务")
async def trigger_yahoo_stock_update(background_tasks: BackgroundTasks):
    """
    手动触发后台任务，从Yahoo Finance全量同步股票数据到本地数据库。
    如果任务正在运行，则直接返回状态说明。
    """
    if YahooSyncService.is_running():
        return BaseResponse.success(message="Task is already running", data={"status": "running"})
    
    background_tasks.add_task(YahooSyncService.sync_all_stocks)
    return BaseResponse.success(message="Task started", data={"status": "started"})

@router.post("/task/yahoo_stock_status", response_model=BaseResponse, summary="查询雅虎股票更新任务状态")
async def get_yahoo_stock_status():
    """
    查询当前是否正在进行股票同步任务。
    """
    is_running = YahooSyncService.is_running()
    return BaseResponse.success(data={"is_running": is_running})
