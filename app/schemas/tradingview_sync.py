from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field

class TradingViewStockBase(BaseModel):
    stock_symbol: str
    tradingview_full_stock_symbol: str
    exchange_acronym: str
    name: str = ""
    description: str = ""
    logoid: Optional[str] = None
    logo_url: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class TradingViewStockListResponse(BaseModel):
    total: int
    data: List[TradingViewStockBase]

class SyncTaskStatus(BaseModel):
    is_running: bool
    status: str
    processed_count: int
    total_count: int = 0
    last_error: Optional[str] = None
    last_run_time: Optional[datetime] = None
