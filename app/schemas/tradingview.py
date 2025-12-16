from enum import Enum
from typing import List, Optional, Any
from pydantic import BaseModel, Field

class IntervalEnum(str, Enum):
    ONEMINUTE = "1m"
    FIVEMINUTES = "5m"
    FIFTEENMINUTES = "15m"
    THIRTYMINUTES = "30m"
    ONEHOUR = "1h"
    TWOHOURS = "2h"
    FOURHOURS = "4h"
    ONEDAY = "1d"
    ONEWEEK = "1W"
    ONEMONTH = "1M"

class ScreenerEnum(str, Enum):
    AMERICA = "america"
    INDONESIA = "indonesia"
    INDIA = "india"
    UK = "uk"
    BRAZIL = "brazil"
    VIETNAM = "vietnam"
    RSA = "rsa"
    KSA = "ksa"
    AUSTRALIA = "australia"
    RUSSIA = "russia"
    THAILAND = "thailand"
    PHILIPPINES = "philippines"
    TAIWAN = "taiwan"
    TURKEY = "turkey"
    FRANCE = "france"
    GERMANY = "germany"
    ITALY = "italy"
    SPAIN = "spain"
    PORTUGAL = "portugal"
    POLAND = "poland"
    NETHERLANDS = "netherlands"
    BELGIUM = "belgium"
    SWITZERLAND = "switzerland"
    SWEDEN = "sweden"
    NORWAY = "norway"
    DENMARK = "denmark"
    FINLAND = "finland"
    GREECE = "greece"
    ISRAEL = "israel"
    UAE = "uae"
    QATAR = "qatar"
    BAHRAIN = "bahrain"
    OMAN = "oman"
    KUWAIT = "kuwait"
    EGYPT = "egypt"
    CRYPTO = "crypto"
    FOREX = "forex"
    CFD = "cfd"

class AnalysisRequest(BaseModel):
    symbol: str = Field(..., description="Ticker symbol or pair. Examples: 'AAPL', 'BTCUSDT', 'EURUSD'", examples=["AAPL", "BTCUSDT"])
    screener: ScreenerEnum = Field(..., description="Screener country or market type. Select 'america' for US stocks, 'crypto' for cryptocurrencies.", examples=["america", "crypto"])
    exchange: str = Field(..., description="Exchange name. Examples: 'NASDAQ', 'NYSE', 'BINANCE', 'FX_IDC'", examples=["NASDAQ", "BINANCE"])
    interval: IntervalEnum = Field(default=IntervalEnum.ONEDAY, description="Time interval for analysis.", examples=["1d", "1h"])

class MultipleAnalysisRequest(BaseModel):
    symbols: List[str] = Field(..., description="List of symbols prefixed with exchange. Examples: ['NASDAQ:AAPL', 'BINANCE:BTCUSDT']", examples=[["NASDAQ:AAPL", "BINANCE:BTCUSDT"]])
    screener: ScreenerEnum = Field(..., description="Screener (must be consistent for all symbols)", examples=["america", "crypto"])
    interval: IntervalEnum = Field(default=IntervalEnum.ONEDAY, description="Time interval", examples=["1d"])

class SearchTypeEnum(str, Enum):
    STOCK = "stock"
    CRYPTO = "crypto"
    FUTURES = "futures"
    INDEX = "index"
    FOREX = "forex"
    CFD = "cfd"
    FUND = "fund"

class SearchRequest(BaseModel):
    text: str = Field(..., description="Search query string", examples=["BTC", "Apple"])
    type: Optional[SearchTypeEnum] = Field(default=None, description="Filter by asset type", examples=["crypto", "stock"])
