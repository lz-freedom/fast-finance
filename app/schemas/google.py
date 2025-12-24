from enum import Enum
from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, Field, ConfigDict

# --- Enums ---

class GoogleHistoryRange(str, Enum):
    d1 = "1d"   # 1 Minute Interval
    d5 = "5d"   # 30 Minute Interval
    mo1 = "1mo" # Daily Interval
    mo6 = "6mo" # Daily Interval
    ytd = "ytd" # Daily Interval
    y1 = "1y"   # Daily Interval
    y5 = "5y"   # Weekly Interval
    max = "max" # Weekly Interval

# --- Request Models ---

class GoogleSearchRequest(BaseModel):
    query: str = Field(..., description="搜索关键词 / Search Query", example="Apple")

class GoogleDetailRequest(BaseModel):
    symbol: str = Field(..., description="股票代码 / Stock Symbol", example="AAPL")
    exchange: str = Field(..., description="交易所代码 / Exchange Code", example="NASDAQ")

class GoogleDetailItem(BaseModel):
    symbol: str = Field(..., description="股票代码", example="AAPL")
    exchange: str = Field(..., description="交易所代码", example="NASDAQ")

class GoogleDetailsRequest(BaseModel):
    symbols: List[GoogleDetailItem] = Field(..., description="股票列表", example=[{"symbol": "AAPL", "exchange": "NASDAQ"}])

class GoogleHistoryRequest(BaseModel):
    symbol: str = Field(..., description="股票代码 / Stock Symbol", example="AAPL")
    exchange: str = Field(..., description="交易所代码 / Exchange Code", example="NASDAQ")
    range: GoogleHistoryRange = Field(default=GoogleHistoryRange.mo1, description="时间范围 / Time Range")

# --- Response Models ---

class GoogleSearchResponse(BaseModel):
    model_config = ConfigDict(extra='allow')
    
    code: Optional[str] = Field(None, description="股票代码")
    exchange: Optional[str] = Field(None, description="交易所")
    name: Optional[str] = Field(None, description="名称")
    type: Optional[str] = Field(None, description="类型")
    region: Optional[str] = Field(None, description="地区")

class GoogleDetailResponse(BaseModel):
    model_config = ConfigDict(extra='allow')
    
    code: Optional[str] = None
    exchange: Optional[str] = None
    name: Optional[str] = None
    currency: Optional[str] = None
    last_price: Optional[float] = None
    change: Optional[float] = None
    change_percent: Optional[float] = None
    update_time: Optional[str] = None

class GoogleHistoryItem(BaseModel):
    date: str
    close: Optional[float] = None
    volume: Optional[int] = None

class GoogleHistoryResponse(BaseModel):
    symbol: str
    exchange: str
    range: str
    data: List[GoogleHistoryItem]

# --- Scraping Models ---

class GoogleScrapeRequest(BaseModel):
    symbol: str = Field(..., description="股票代码 / Stock Symbol", example="AAPL")
    exchange: str = Field(..., description="交易所代码 / Exchange Code", example="NASDAQ")

class GooglePeer(BaseModel):
    symbol: str
    name: str
    price: Optional[str] = None
    change_percent: Optional[str] = None

class GoogleScrapeResponse(BaseModel):
    symbol: str
    exchange: str
    price: Optional[str] = None
    currency: Optional[str] = None
    change_percent: Optional[str] = None
    stats: Dict[str, Optional[str]] = Field(default_factory=dict, description="Key Statistics like Market Cap, Volume")
    about: Dict[str, Optional[str]] = Field(default_factory=dict, description="Company Description and Details")
    peers: List[GooglePeer] = Field(default_factory=list, description="Related Stocks")
