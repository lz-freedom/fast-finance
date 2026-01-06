from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
from datetime import datetime

from app.schemas.tradingview_sync import TradingViewStockListResponse, TradingViewStockBase, SyncTaskStatus
from app.services.tradingview_sync_service import tradingview_sync_service
from app.core.database import DBManager

router = APIRouter()

from app.schemas.response import BaseResponse

from pydantic import BaseModel

class StockFilter(BaseModel):
    exchange_acronym: Optional[str] = None
    min_created_at: Optional[datetime] = None

class StartSyncRequest(BaseModel):
    ipo_offer_date_type: Optional[str] = None

@router.post("/sync/start", response_model=BaseResponse[SyncTaskStatus], summary="启动同步任务", description="启动 TradingView 股票数据同步任务")
def start_sync_task(request: StartSyncRequest = StartSyncRequest()):
    """
    启动 TradingView 股票数据同步任务。
    可选参数: ipo_offer_date_type (day, yesterday, week, month, year)
    """
    status = tradingview_sync_service.start_sync_task(request.ipo_offer_date_type)
    return BaseResponse.success(data=status)

@router.post("/sync/status", response_model=BaseResponse[SyncTaskStatus], summary="获取同步状态", description="查询当前同步任务的运行状态")
def get_sync_status():
    """
    查询当前同步任务的运行状态。
    """
    status = tradingview_sync_service.get_task_status()
    return BaseResponse.success(data=status)

@router.post("/stocks", response_model=BaseResponse[List[dict]], summary="获取股票列表", description="查询已同步的 TradingView 股票数据") 
def get_tradingview_stocks(
    filter_req: StockFilter = StockFilter()
):
    """
    查询已同步的 TradingView 股票数据。
    支持按交易所简称 (exchange_acronym) 和创建时间 (min_created_at) 进行过滤。
    """
    stocks = DBManager.get_tradingview_stocks(filter_req.exchange_acronym, filter_req.min_created_at)
    return BaseResponse.success(data=stocks)
