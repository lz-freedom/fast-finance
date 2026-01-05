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

class FinancialsFrequency(str, Enum):
    yearly = "yearly"
    quarterly = "quarterly"

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
    freq: FinancialsFrequency = Field(default=FinancialsFrequency.yearly, description="频率 / Frequency")

class YahooSplitsRequest(BaseModel):
    symbol: str = Field(..., description="股票代码 / Stock Symbol", example="AAPL")
    period: YahooPeriod = Field(default=YahooPeriod.max, description="时间周期 / Time Period")

class YahooDividendsRequest(BaseModel):
    symbol: str = Field(..., description="股票代码 / Stock Symbol", example="AAPL")
    period: YahooPeriod = Field(default=YahooPeriod.max, description="时间周期 / Time Period")

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


class StockBaseDataRequestItem(BaseModel):
    stock_symbol: str = Field(..., description="股票代码", example="AAPL")
    exchange_acronym: str = Field(..., description="交易所缩写", example="NAS")

class StockBaseDataBatchRequest(BaseModel):
    is_return_history: bool = Field(False, description="是否返回历史K线数据")
    stock_list: List[StockBaseDataRequestItem] = Field(..., description="股票列表")

    model_config = {
        "json_schema_extra": {
            "example": {
                "is_return_history": False,
                "stock_list": [
                    {
                        "stock_symbol": "AAPL",
                        "exchange_acronym": "NASDAQ"
                    },
                    {
                        "stock_symbol": "NVDA",
                        "exchange_acronym": "NASDAQ"
                    },
                    {
                        "stock_symbol": "601933",
                        "exchange_acronym": "SSE"
                    }
                ]
            }
        }
    }

class CompanyOfficer(BaseModel):
    name: Optional[str] = None
    age: Optional[int] = None
    birth_year: Optional[int] = None
    total_pay: Optional[int] = None

class StockBaseDataResponseItem(BaseModel):
    model_config = ConfigDict(extra='allow')

    symbol: str = Field(..., description="股票代码")
    exchange_acronym: str = Field(..., description="交易所缩写")
    yahoo_symbol: str = Field(..., description="Yahoo股票代码")
    yahoo_exchange: Optional[str] = Field(None, description="Yahoo交易所代码")
    
    # Basic Info
    name: Optional[str] = Field(None, description="股票名称")
    exchange_timezone_name: Optional[str] = Field(None, description="交易所时区")
    exchange_timezone_short_name: Optional[str] = Field(None, description="时区缩写")
    gmt_off_set_milliseconds: Optional[int] = Field(None, description="时区偏移")
    currency: Optional[str] = Field(None, description="计价货币")
    
    # Profile
    long_business_summary: Optional[str] = Field(None, description="长业务总结")
    sector: Optional[str] = Field(None, description="行业")
    industry: Optional[str] = Field(None, description="业务摘要")
    country: Optional[str] = Field(None, description="国家")
    state: Optional[str] = Field(None, description="州")
    city: Optional[str] = Field(None, description="城市")
    zip: Optional[str] = Field(None, description="邮编")
    address_line_1: Optional[str] = Field(None, description="详细地址第一行")
    address_line_2: Optional[str] = Field(None, description="详细地址第二行")
    phone: Optional[str] = Field(None, description="电话")
    full_time_employees: Optional[int] = Field(None, description="全职员工数量")
    website: Optional[str] = Field(None, description="官网")
    investor_relations_website: Optional[str] = Field(None, description="面向投资者的官网")
    ceo_info: Optional[CompanyOfficer] = Field(None, description="CEO信息")
    
    # Market Data
    market_state: Optional[str] = Field(None, description="市场状态（PRE/REGULAR/POST）")
    current_price: Optional[float] = Field(None, description="当前价格")
    previous_close: Optional[float] = Field(None, description="前一交易日收盘价")
    open: Optional[float] = Field(None, description="开盘价")
    day_low: Optional[float] = Field(None, description="今日最低价")
    day_high: Optional[float] = Field(None, description="今日最高价")
    volume: Optional[int] = Field(None, description="当日成交量")
    turnover: Optional[float] = Field(None, description="成交额")
    regular_market_volume: Optional[int] = Field(None, description="正常交易时段成交量")
    regular_market_previous_close: Optional[float] = Field(None, description="正常交易时段前收盘")
    regular_market_open: Optional[float] = Field(None, description="正常交易时段开盘价")
    regular_market_day_low: Optional[float] = Field(None, description="正常交易时段最低价")
    regular_market_day_high: Optional[float] = Field(None, description="正常交易时段最高价")
    
    bid: Optional[float] = Field(None, description="买一价")
    ask: Optional[float] = Field(None, description="卖一价")
    bid_size: Optional[int] = Field(None, description="买一档数量")
    ask_size: Optional[int] = Field(None, description="卖一档数量")
    
    # Valuation & Ratios
    market_cap: Optional[int] = Field(None, description="总市值")
    enterprise_value: Optional[int] = Field(None, description="企业价值（EV）")
    beta: Optional[float] = Field(None, description="Beta值")
    pe_ttm: Optional[float] = Field(None, description="市盈率（TTM）")
    pe_static: Optional[float] = Field(None, description="市盈率 (静)")
    pe_dynamic: Optional[float] = Field(None, description="市盈率 (动)")
    price_to_sales_trailing_12_months: Optional[float] = Field(None, description="市销率（TTM）")
    price_to_book: Optional[float] = Field(None, description="市净率")
    trailing_peg_ratio: Optional[float] = Field(None, description="PEG（市盈率 / 增长率）")
    
    # Dividends
    dividend_rate: Optional[float] = Field(None, description="年化股息金额")
    dividend_yield: Optional[float] = Field(None, description="当前股息率（%）")
    ex_dividend_date: Optional[int] = Field(None, description="除息日")
    payout_ratio: Optional[float] = Field(None, description="分红支付率")
    five_year_avg_dividend_yield: Optional[float] = Field(None, description="5 年平均股息率")
    last_dividend_value: Optional[float] = Field(None, description="最近一次派息金额")
    last_dividend_date: Optional[int] = Field(None, description="最近一次派息日期")
    trailing_annual_dividend_rate: Optional[float] = Field(None, description="过去 12 个月分红金额")
    trailing_annual_dividend_yield: Optional[float] = Field(None, description="过去 12 个月股息率")
    dividend_ttm: Optional[float] = Field(None, description="股息 TTM")
    dividend_yield_ttm: Optional[float] = Field(None, description="股息率 TTM")

    # Financials
    total_revenue: Optional[int] = Field(None, description="总营收")
    revenue_per_share: Optional[float] = Field(None, description="每股营收")
    revenue_growth: Optional[float] = Field(None, description="营收同比增长率")
    net_income_to_common: Optional[int] = Field(None, description="归母净利润")
    earnings_growth: Optional[float] = Field(None, description="盈利增长率")
    earnings_quarterly_growth: Optional[float] = Field(None, description="季度盈利增长")
    ebitda: Optional[int] = Field(None, description="EBITDA")
    enterprise_to_revenue: Optional[float] = Field(None, description="EV / Revenue")
    enterprise_to_ebitda: Optional[float] = Field(None, description="EV / EBITDA")
    profit_margin: Optional[float] = Field(None, description="净利润率")
    gross_margin: Optional[float] = Field(None, description="毛利润率")
    ebitda_margin: Optional[float] = Field(None, description="EBITDA 利润率")
    operating_margin: Optional[float] = Field(None, description="营业利润率")
    return_on_assets: Optional[float] = Field(None, description="ROA")
    return_on_equity: Optional[float] = Field(None, description="ROE")
    free_cashflow: Optional[int] = Field(None, description="自由现金流")
    operating_cashflow: Optional[int] = Field(None, description="经营现金流")
    total_cash: Optional[int] = Field(None, description="现金及等价物")
    total_cash_per_share: Optional[float] = Field(None, description="每股现金")
    total_debt: Optional[int] = Field(None, description="总负债")
    debt_to_equity: Optional[float] = Field(None, description="资产负债率")

    # EPS
    trailing_eps: Optional[float] = Field(None, description="静态每股收益（TTM）")
    forward_eps: Optional[float] = Field(None, description="预测每股收益")
    eps_trailing_twelve_months: Optional[float] = Field(None, description="过去 12 个月 EPS")
    eps_forward: Optional[float] = Field(None, description="未来 EPS")
    eps_current_year: Optional[float] = Field(None, description="当年 EPS 预测")
    price_eps_current_year: Optional[float] = Field(None, description="当前价 / 当年 EPS")

    # Ownership & Short Interest
    held_percent_insiders: Optional[float] = Field(None, description="内部人持股比例")
    held_percent_institutions: Optional[float] = Field(None, description="机构持股比例")
    shares_short: Optional[int] = Field(None, description="当前卖空股数")
    shares_short_prior_month: Optional[int] = Field(None, description="上月卖空股数")
    shares_short_previous_month_date: Optional[int] = Field(None, description="上月卖空统计时间")
    date_short_interest: Optional[int] = Field(None, description="卖空数据日期")
    shares_percent_shares_out: Optional[float] = Field(None, description="卖空占总股本比例")
    short_ratio: Optional[float] = Field(None, description="空头回补天数")
    short_percent_of_float: Optional[float] = Field(None, description="卖空占流通股比例")
    
    # Shares
    float_shares: Optional[int] = Field(None, description="流通股数")
    shares_outstanding: Optional[int] = Field(None, description="总股本")
    implied_shares_outstanding: Optional[int] = Field(None, description="推算流通股数")
    last_split_factor: Optional[str] = Field(None, description="最近一次拆股比例")
    last_split_date: Optional[int] = Field(None, description="拆股日期")

    # Price Statistics
    average_volume: Optional[int] = Field(None, description="平均日成交量")
    average_volume_10days: Optional[int] = Field(None, description="10日平均成交量")
    average_daily_volume_10day: Optional[int] = Field(None, description="10日平均成交量 (重复)")
    fifty_two_week_low: Optional[float] = Field(None, description="52 周最低价")
    fifty_two_week_high: Optional[float] = Field(None, description="52 周最高价")
    all_time_high: Optional[float] = Field(None, description="历史最高价")
    all_time_low: Optional[float] = Field(None, description="历史最低价")
    fifty_two_week_range: Optional[str] = Field(None, description="52 周价格区间")
    fifty_two_week_change_percent: Optional[float] = Field(None, description="52 周涨跌幅")
    sand_p_52_week_change: Optional[float] = Field(None, description="标普 500 52 周涨跌幅")
    fifty_day_average: Optional[float] = Field(None, description="50日均线")
    two_hundred_day_average: Optional[float] = Field(None, description="200日均线")
    fifty_day_average_change: Optional[float] = Field(None, description="当前价 vs 50日均线")
    fifty_day_average_change_percent: Optional[float] = Field(None, description="与50日均线偏离率")
    two_hundred_day_average_change: Optional[float] = Field(None, description="当前价 vs 200日均线")
    two_hundred_day_average_change_percent: Optional[float] = Field(None, description="与 200 日均线偏离率")
    
    # Price Statistics Extras
    turnover_rate: Optional[float] = Field(None, description="换手率")
    turnover_value: Optional[float] = Field(None, description="流通值")
    amplitude: Optional[float] = Field(None, description="振幅")
    volume_ratio: Optional[float] = Field(None, description="量比")
    average_price: Optional[float] = Field(None, description="平均价")
    
    # Pre/Post Market
    pre_market_price: Optional[float] = Field(None, description="盘前价格")
    pre_market_change: Optional[float] = Field(None, description="盘前涨跌额")
    pre_market_change_percent: Optional[float] = Field(None, description="盘前涨跌幅")
    pre_market_time: Optional[int] = Field(None, description="盘前时间戳")
    post_market_change_percent: Optional[float] = Field(None, description="盘后涨跌幅")
    post_market_price: Optional[float] = Field(None, description="盘后价格")
    post_market_change: Optional[float] = Field(None, description="盘后涨跌额")
    post_market_time: Optional[int] = Field(None, description="盘后时间")
    
    # Calculated Returns
    year_to_date_return: Optional[float] = Field(None, description="年初至今回报率")
    year_to_date_trading_date_range: Optional[str] = Field(None, description="年初至今交易日区间")
    
    three_month_return: Optional[float] = Field(None, description="近3个月回报率")
    three_month_trading_date_range: Optional[str] = Field(None, description="近3个月交易日区间")
    
    six_month_return: Optional[float] = Field(None, description="近6个月回报率")
    six_month_trading_date_range: Optional[str] = Field(None, description="近6个月交易日区间")
    
    one_year_return: Optional[float] = Field(None, description="近1年回报率")
    one_year_trading_date_range: Optional[str] = Field(None, description="近1年交易日区间")
    
    three_year_return: Optional[float] = Field(None, description="近3年回报率")
    three_year_trading_date_range: Optional[str] = Field(None, description="近3年交易日区间")
    
    five_year_return: Optional[float] = Field(None, description="近5年回报率")
    five_year_trading_date_range: Optional[str] = Field(None, description="近5年交易日区间")
    
    # History
    history: Optional[List[Dict[str, Any]]] = Field(None, description="近5年历史K线")


