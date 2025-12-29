from fastapi import APIRouter
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel

from app.schemas.response import BaseResponse
from app.schemas.tradingview_sync import SyncTaskStatus
from app.services.investing_sync_service import investing_sync_service
from app.core.database import SQLiteManager

router = APIRouter()

class StockFilter(BaseModel):
    exchange_acronym: Optional[str] = None
    min_created_at: Optional[datetime] = None

@router.post("/sync/start", response_model=BaseResponse[SyncTaskStatus], summary="启动同步任务", description="启动 Investing.com 股票数据同步任务")
def start_sync_task():
    """
    启动 Investing.com 股票数据同步任务 (后台运行)。
    """
    status = investing_sync_service.start_sync_task()
    return BaseResponse.success(data=status)

@router.post("/sync/status", response_model=BaseResponse[SyncTaskStatus], summary="获取同步状态", description="查询当前 Investing.com 同步任务的运行状态")
def get_sync_status():
    """
    查询当前同步任务的运行状态。
    """
    status = investing_sync_service.get_task_status()
    return BaseResponse.success(data=status)

@router.post("/stocks", response_model=BaseResponse[List[dict]], summary="获取股票列表", description="查询已同步的 Investing.com 股票数据") 
def get_investing_stocks(
    filter_req: StockFilter = StockFilter()
):
    """
    查询已同步的 Investing.com 股票数据。
    """
    # SQLiteManager needs a method to get investing stocks
    # Need to add get_investing_stocks to SQLiteManager first? 
    # Or just execute query here? Better add to Manager.
    # I'll add the method to SQLiteManager in the next step.
    stocks = SQLiteManager.get_investing_stocks(filter_req.exchange_acronym, filter_req.min_created_at)
    return BaseResponse.success(data=stocks)
