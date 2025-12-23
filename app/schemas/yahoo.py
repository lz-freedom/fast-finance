from enum import Enum
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict

# --- Enums ---

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
    symbol: str = Field(..., description="股票代码 / Stock Symbol", example="AAPL")

class YahooHistoryRequest(BaseModel):
    symbol: str = Field(..., description="股票代码 / Stock Symbol", example="AAPL")
    period: YahooPeriod = Field(default=YahooPeriod.mo1, description="时间周期 / Time Period")
    interval: YahooInterval = Field(default=YahooInterval.d1, description="K线间隔 / Interval")

class YahooFinancialsRequest(BaseModel):
    symbol: str = Field(..., description="股票代码 / Stock Symbol", example="AAPL")
    type: FinancialsType = Field(..., description="报表类型 / Report Type")

class YahooSearchRequest(BaseModel):
    query: str = Field(..., description="搜索关键词 / Search Query", example="Apple")

class YahooNewsRequest(BaseModel):
    symbol: str = Field(..., description="股票代码 / Stock Symbol", example="AAPL")

class YahooHoldersRequest(BaseModel):
    symbol: str = Field(..., description="股票代码 / Stock Symbol", example="AAPL")

class YahooAnalysisRequest(BaseModel):
    symbol: str = Field(..., description="股票代码 / Stock Symbol", example="AAPL")

class YahooCalendarRequest(BaseModel):
    symbol: str = Field(..., description="股票代码 / Stock Symbol", example="AAPL")

# --- Response Models ---

class YahooTickerInfo(BaseModel):
    model_config = ConfigDict(extra='allow')
    
    symbol: Optional[str] = Field(None, description="股票代码", example="AAPL")
    shortName: Optional[str] = Field(None, description="股票简称", example="Apple Inc.")
    longName: Optional[str] = Field(None, description="股票全称", example="Apple Inc.")
    currency: Optional[str] = Field(None, description="货币单位", example="USD")
    exchange: Optional[str] = Field(None, description="交易所", example="NMS")
    quoteType: Optional[str] = Field(None, description="标的类型", example="EQUITY")
    
    # Market Data
    currentPrice: Optional[float] = Field(None, description="当前价格", example=150.25)
    open: Optional[float] = Field(None, description="今日开盘价", example=148.0)
    dayHigh: Optional[float] = Field(None, description="今日最高", example=151.0)
    dayLow: Optional[float] = Field(None, description="今日最低", example=147.5)
    previousClose: Optional[float] = Field(None, description="昨收", example=149.0)
    volume: Optional[int] = Field(None, description="成交量", example=50000000)
    marketCap: Optional[int] = Field(None, description="市值", example=2500000000000)
    
    # Fundamentals
    trailingPE: Optional[float] = Field(None, description="市盈率 (TTM)", example=28.5)
    forwardPE: Optional[float] = Field(None, description="预测市盈率", example=25.0)
    dividendYield: Optional[float] = Field(None, description="股息率", example=0.005)
    dividendRate: Optional[float] = Field(None, description="每股股息", example=0.8)
    exDividendDate: Optional[int] = Field(None, description="除息日 (Timestamp)", example=1675987200)
    targetMeanPrice: Optional[float] = Field(None, description="分析师目标均价", example=180.0)

class HistoricalDataItem(BaseModel):
    model_config = ConfigDict(extra='allow')
    
    date: str = Field(..., description="日期 (ISO)", example="2023-10-01T00:00:00")
    open: Optional[float] = Field(None, description="开盘价")
    high: Optional[float] = Field(None, description="最高价")
    low: Optional[float] = Field(None, description="最低价")
    close: Optional[float] = Field(None, description="收盘价")
    volume: Optional[int] = Field(None, description="成交量")

class YahooSearchResult(BaseModel):
    symbol: str
    shortname: Optional[str] = None
    longname: Optional[str] = None
    exchange: Optional[str] = None
    type: Optional[str] = None

class YahooSearchResponse(BaseModel):
    query: str
    count: int
    results: List[YahooSearchResult]

class YahooNewsItem(BaseModel):
    model_config = ConfigDict(extra='allow')
    
    uuid: Optional[str] = None
    title: Optional[str] = None
    publisher: Optional[str] = None
    link: Optional[str] = None
    providerPublishTime: Optional[int] = None
    type: Optional[str] = None

class YahooHoldersResponse(BaseModel):
    model_config = ConfigDict(
        extra='allow',
        json_schema_extra={
            "example": {
                "majorHolders": [{"maxAge": 1, "value": 0.5, "breakdown": "insiders"}],
                "institutionalHolders": [{"maxAge": 1, "organization": "Vanguard", "value": 123456}],
                "mutualfundHolders": [{"maxAge": 1, "organization": "Vanguard 500", "value": 654321}]
            }
        }
    )
    
    majorHolders: Optional[List[Dict[str, Any]]] = Field(None, description="主要股东 (Insiders)")
    institutionalHolders: Optional[List[Dict[str, Any]]] = Field(None, description="机构持有者")
    mutualfundHolders: Optional[List[Dict[str, Any]]] = Field(None, description="公募基金持有者")

class YahooAnalysisResponse(BaseModel):
    model_config = ConfigDict(
        extra='allow',
        json_schema_extra={
            "example": {
                "recommendationsSummary": [
                    {"period": "0m", "strongbuy": 5, "buy": 24, "hold": 15, "sell": 1, "strongsell": 3},
                    {"period": "-1m", "strongbuy": 5, "buy": 24, "hold": 15, "sell": 1, "strongsell": 3}
                ],
                "recommendations": [
                    {"period": "0m", "strongbuy": 4, "buy": 10, "hold": 0, "sell": 0, "strongsell": 0}
                ],
                "targetMean": 180.5,
                "upgradesDowngrades": [
                    {"gradeDate": "2023-10-01", "action": "main", "fromGrade": "Buy", "toGrade": "Strong Buy", "firm": "SomeFirm"}
                ]
            }
        }
    )
    
    recommendations: Optional[List[Dict[str, Any]]] = Field(None, description="近期评级推荐")
    recommendationsSummary: Optional[List[Dict[str, Any]]] = Field(None, description="评级汇总 (Strong Buy etc.)")
    targetMean: Optional[float] = Field(None, description="目标均价")
    upgradesDowngrades: Optional[List[Dict[str, Any]]] = Field(None, description="评级升降级记录")


class YahooCalendarResponse(BaseModel):
    model_config = ConfigDict(extra='allow')
    
    calendar: Optional[Dict[str, Any]] = Field(None, description="财报日历等信息")

class YahooMarketActivesRequest(BaseModel):
    regions: List[str] = Field(..., description="国家地区列表 / Regions List", example=["us", "cn", "sg", "hk", "in"])
    minIntradayMarketCap: int = Field(20000000, description="盘中市值最小值 / Min Intraday Market Cap")
    minDayVolume: int = Field(5000000, description="日交易量最小值 / Min Day Volume")
    exchanges: List[str] = Field(..., description="交易所列表 / Exchanges List", example=['SHH','SHZ','HKG','NYQ','NMS','SES','JPX','NSI','LSE','TOR','VAN','ASX'])
    size: int = Field(10, description="返回条数 / Size per region")

class YahooMarketActivesResponse(BaseModel):
    data: Dict[str, List[Dict[str, Any]]] = Field(..., description="各地区股票列表 / Market Data by Region")

