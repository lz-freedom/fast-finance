from enum import Enum
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

class YahooInterval(str, Enum):
    m1 = "1m"
    m2 = "2m"
    m5 = "5m"
    m15 = "15m"
    m30 = "30m"
    m60 = "60m"
    m90 = "90m"
    h1 = "1h"
    d1 = "1d"
    d5 = "5d"
    wk1 = "1wk"
    mo1 = "1mo"
    mo3 = "3mo"

class YahooPeriod(str, Enum):
    d1 = "1d"
    d5 = "5d"
    mo1 = "1mo"
    mo3 = "3mo"
    mo6 = "6mo"
    y1 = "1y"
    y2 = "2y"
    y5 = "5y"
    y10 = "10y"
    ytd = "ytd"
    max = "max"

class FinancialsType(str, Enum):
    balance = "balance"
    income = "income"
    cashflow = "cashflow"

# --- Request Models ---

class YahooInfoRequest(BaseModel):
    symbol: str = Field(..., description="股票代码", example="AAPL")

class YahooHistoryRequest(BaseModel):
    symbol: str = Field(..., description="股票代码", example="AAPL")
    period: YahooPeriod = Field(default=YahooPeriod.mo1, description="时间周期")
    interval: YahooInterval = Field(default=YahooInterval.d1, description="K线间隔")

class YahooFinancialsRequest(BaseModel):
    symbol: str = Field(..., description="股票代码", example="AAPL")
    type: FinancialsType = Field(..., description="报表类型: balance, income, cashflow")

class YahooSearchRequest(BaseModel):
    query: str = Field(..., description="搜索关键词", example="Apple")

class YahooNewsRequest(BaseModel):
    symbol: str = Field(..., description="股票代码", example="AAPL")

class YahooHoldersRequest(BaseModel):
    symbol: str = Field(..., description="股票代码", example="AAPL")

class YahooAnalysisRequest(BaseModel):
    symbol: str = Field(..., description="股票代码", example="AAPL")

class YahooCalendarRequest(BaseModel):
    symbol: str = Field(..., description="股票代码", example="AAPL")

# --- Response Models ---

class HistoricalDataInternal(BaseModel):
    date: str
    open: Optional[float]
    high: Optional[float]
    low: Optional[float]
    close: Optional[float]
    volume: Optional[int]

class TickerInfoResponse(BaseModel):
    symbol: str
    info: Dict[str, Any]

class HistoryResponse(BaseModel):
    symbol: str
    period: str
    interval: str
    data: List[HistoricalDataInternal]

class SearchResult(BaseModel):
    symbol: str
    shortname: Optional[str] = None
    longname: Optional[str] = None
    exchange: Optional[str] = None
    type: Optional[str] = None

class SearchResponse(BaseModel):
    query: str
    count: int
    results: List[SearchResult]

class NewsItem(BaseModel):
    uuid: Optional[str] = None
    title: Optional[str] = None
    publisher: Optional[str] = None
    link: Optional[str] = None
    providerPublishTime: Optional[int] = None
    type: Optional[str] = None
    thumbnail: Optional[Dict] = None
    relatedTickers: Optional[List[str]] = None

class HoldersResponse(BaseModel):
    major_holders: Optional[Dict[str, Any]] = None
    institutional_holders: Optional[List[Dict[str, Any]]] = None
    mutualfund_holders: Optional[List[Dict[str, Any]]] = None

class AnalysisResponse(BaseModel):
    recommendations: Optional[List[Dict[str, Any]]] = None
    recommendations_summary: Optional[Dict[str, Any]] = None
    target_mean: Optional[float] = None
    upgrades_downgrades: Optional[List[Dict[str, Any]]] = None

class CalendarResponse(BaseModel):
    calendar: Optional[Dict[str, Any]] = None
