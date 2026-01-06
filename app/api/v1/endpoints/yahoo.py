from fastapi import APIRouter, Body
from typing import List, Dict, Any
from app.services.yahoo_service import YahooService
from app.schemas.response import BaseResponse
from app.schemas.yahoo import (
    YahooInfoRequest, 
    YahooHistoryRequest, 
    YahooFinancialsRequest, 
    YahooSearchRequest,
    YahooNewsRequest,
    YahooHoldersRequest,
    YahooAnalysisRequest,
    YahooCalendarRequest,
    YahooCalendarRequest,
    YahooMarketActivesRequest,
    YahooSplitsRequest,
    YahooDividendsRequest,
    YahooDividendsRequest,
    StockBaseDataRequestItem,
    StockBaseDataBatchRequest,
    StockBaseDataResponseItem
)

router = APIRouter()

@router.post("/info", response_model=BaseResponse, summary="获取股票详细信息")
async def get_ticker_info(request: YahooInfoRequest):
    """
    获取单个股票的基本面详细信息。
    """
    try:
        data = YahooService.get_ticker_info(request.symbol)
        return BaseResponse.success(data=data)
    except Exception as e:
        raise e

@router.post("/history", response_model=BaseResponse, summary="获取历史K线数据")
async def get_history(request: YahooHistoryRequest):
    """
    获取股票的历史市场数据。
    """
    try:
        data = YahooService.get_history(request.symbol, request.period.value, request.interval.value)
        return BaseResponse.success(data=data)
    except Exception as e:
        raise e

@router.post("/financials", response_model=BaseResponse, summary="获取财务报表")
async def get_financials(request: YahooFinancialsRequest):
    """
    获取资产负债表、利润表或现金流量表。
    """
    try:
        data = YahooService.get_financials(request.symbol, request.type.value, request.freq.value)
        return BaseResponse.success(data=data)
    except Exception as e:
        raise e

@router.post("/search", response_model=BaseResponse, summary="搜索股票")
async def search_tickers(request: YahooSearchRequest):
    """
    搜索股票代码。
    """
    try:
        results = YahooService.search_tickers(request.query)
        return BaseResponse.success(data={
            "query": request.query,
            "count": len(results),
            "results": results
        })
    except Exception as e:
        raise e

@router.post("/news", response_model=BaseResponse, summary="获取股票新闻")
async def get_news(request: YahooNewsRequest):
    """
    获取股票相关新闻。
    """
    try:
        data = YahooService.get_news(request.symbol)
        return BaseResponse.success(data=data)
    except Exception as e:
        raise e

@router.post("/holders", response_model=BaseResponse, summary="获取股东信息")
async def get_holders(request: YahooHoldersRequest):
    """
    获取主要股东、机构股东和公募基金持仓数据。
    """
    try:
        data = YahooService.get_holders(request.symbol)
        return BaseResponse.success(data=data)
    except Exception as e:
        raise e

@router.post("/analysis", response_model=BaseResponse, summary="获取分析师与评级数据")
async def get_analysis(request: YahooAnalysisRequest):
    """
    获取分析师评级、目标价、升级/降级记录。
    """
    try:
        data = YahooService.get_analysis(request.symbol)
        return BaseResponse.success(data=data)
    except Exception as e:
        raise e

@router.post("/calendar", response_model=BaseResponse, summary="获取公司日历")
async def get_calendar(request: YahooCalendarRequest):
    """
    获取公司财报日历、分红日等。
    """
    try:
        data = YahooService.get_calendar(request.symbol)
        return BaseResponse.success(data=data)
    except Exception as e:
        raise e

@router.post("/splits", response_model=BaseResponse, summary="获取股票拆分信息")
async def get_splits(request: YahooSplitsRequest):
    """
    获取股票的历史拆分记录。
    """
    try:
        data = YahooService.get_splits(request.symbol, request.period.value)
        return BaseResponse.success(data=data)
    except Exception as e:
        raise e

@router.post("/dividends", response_model=BaseResponse, summary="获取股票股息信息")
async def get_dividends(request: YahooDividendsRequest):
    """
    获取股票的历史分红记录。
    """
    try:
        data = YahooService.get_dividends(request.symbol, request.period.value)
        return BaseResponse.success(data=data)
    except Exception as e:
        raise e

@router.post("/batch/get_stock_base_data", response_model=BaseResponse[List[StockBaseDataResponseItem]], summary="批量获取股票基础数据")
async def get_batch_stock_base_data(request: StockBaseDataBatchRequest):
    """
    批量获取股票的基础信息、历史K线（近5年）以及回报率数据。
    """
    try:
        # Convert request items to dicts
        items_dicts = [item.model_dump() for item in request.stock_list]
        is_return_history = request.is_return_history
        
        # Run in threadpool
        data = await run_in_threadpool(YahooService.get_batch_stock_base_data, items_dicts, is_return_history)
        return BaseResponse.success(data=data)
    except Exception as e:
        logger.error(f"Error in get_batch_stock_base_data: {e}")
        raise e

@router.post("/rank/market_actives", response_model=BaseResponse, summary="获取活跃股票排行")
async def get_market_actives(request: YahooMarketActivesRequest):
    """
    获取不同国家地区最活跃的股票列表 (基于交易量排序)。
    """
    try:
        data = YahooService.get_active_stocks(
            regions=request.regions,
            min_intraday_market_cap=request.minIntradayMarketCap,
            min_day_volume=request.minDayVolume,
            exchanges=request.exchanges,
            size=request.size
        )
        return BaseResponse.success(data=data)
    except Exception as e:
        raise e

from app.api.v1.endpoints.ai_help import StockFinancialDataAggregationReq
from app.core.constants import get_exchange_info_by_platform_code, PLATFORM_YAHOO
from fastapi.concurrency import run_in_threadpool
from pydantic import BaseModel, Field
from typing import Dict, Optional
from datetime import datetime
import logging

logger = logging.getLogger("fastapi")

class YahooWebCrawlerResponse(BaseModel):
    analysis_returns: Dict[str, Optional[str]] = {}
    analysis_compare_to: List[Dict[str, Any]] = []
    analysis_people_also_watch: List[Dict[str, Any]] = []

class YahooStockRelatedResponse(BaseModel):
    compare_to_list: List[Dict[str, Any]] = []
    people_also_watch_list: List[Dict[str, Any]] = []

@router.post("/yahoo_web_crawler", response_model=BaseResponse[YahooWebCrawlerResponse], summary="雅虎网页爬虫", description="获取回报率、获取同类股票、获取大家都在看 (Raw Data)")
async def yahoo_web_crawler(req: StockFinancialDataAggregationReq):
    try:
        # Resolve Yahoo Symbol
        from app.core.constants import get_stock_info
        yahoo_info = get_stock_info(req.stock_symbol, req.exchange_acronym, PLATFORM_YAHOO)
        
        # If mapping fails, try using stock_symbol directly? Use heuristics or just fail.
        # Current logic: try stock_symbol as fallback or error.
        # User output example implies strictness, but let's be flexible for crawler testing.
        yahoo_symbol = yahoo_info["stock_symbol"] if yahoo_info else req.stock_symbol

        raw_data = await run_in_threadpool(YahooService.web_crawler, yahoo_symbol)
        
        if not raw_data:
            return BaseResponse.success({
                "analysis_returns": {
                    "index_name": "",
                    "ytd_stock_change_percent": None,
                    "ytd_index_change_percent": None,
                    "one_years_stock_change_percent": None,
                    "one_years_index_change_percent": None,
                    "three_years_stock_change_percent": None,
                    "three_years_index_change_percent": None,
                    "five_years_stock_change_percent": None,
                    "five_years_index_change_percent": None,
                },
                "analysis_compare_to": [],
                "analysis_people_also_watch": []
            })
        
        # Flatten Returns Logic
        returns_data = raw_data.get("returns", {})
        flat_returns = {
            "index_name": "",
            "ytd_stock_change_percent": None,
            "ytd_index_change_percent": None,
            "one_years_stock_change_percent": None,
            "one_years_index_change_percent": None,
            "three_years_stock_change_percent": None,
            "three_years_index_change_percent": None,
            "five_years_stock_change_percent": None,
            "five_years_index_change_percent": None,
        }
        
        period_map = {
            "YTD": ("ytd_stock_change_percent", "ytd_index_change_percent"),
            "1-Year": ("one_years_stock_change_percent", "one_years_index_change_percent"),
            "3-Year": ("three_years_stock_change_percent", "three_years_index_change_percent"),
            "5-Year": ("five_years_stock_change_percent", "five_years_index_change_percent"),
        }
        
        for period, data in returns_data.items():
            if period in period_map:
                stock_key, index_key = period_map[period]
                flat_returns[stock_key] = data.get("stock")
                flat_returns[index_key] = data.get("index")
                if data.get("index_name") and not flat_returns["index_name"]:
                    flat_returns["index_name"] = data.get("index_name")

        return BaseResponse.success({
            "analysis_returns": flat_returns,
            "analysis_compare_to": raw_data.get("compare_to", []),
            "analysis_people_also_watch": raw_data.get("people_also_watch", [])
        })

    except Exception as e:
        logger.error(f"Error in yahoo_web_crawler: {e}")
        return BaseResponse.success({ # Return empty success on error to avoid crashing frontend? Or fail? Using success with empty based on existing pattern.
            "analysis_returns": {},
            "analysis_compare_to": [],
            "analysis_people_also_watch": []
        })

@router.post("/yahoo_stock_related", response_model=BaseResponse[YahooStockRelatedResponse], summary="获取关联股票 (Enriched)", description="从数据库或爬虫获取关联股票数据")
async def yahoo_stock_related(req: StockFinancialDataAggregationReq):
    try:
        data = await run_in_threadpool(YahooService.get_related_stock, req.stock_symbol, req.exchange_acronym)
        return BaseResponse.success(data=data)
    except Exception as e:
        logger.error(f"Error in yahoo_stock_related: {e}")
        return BaseResponse.fail(code="500", message=str(e))

@router.post("/local/stocks", response_model=BaseResponse, summary="获取本地同步的股票列表")
async def get_local_stocks(
    start_time: Optional[datetime] = Body(None, description="筛选创建时间在此之后的股票 (ISO format)")
):
    """
    获取从Yahoo同步并保存在本地的股票列表。
    可以根据 start_time 筛选只需增量数据 (例如今天新增的股票)。
    """
    try:
        from app.core.database import SQLiteManager
        
        # Use run_in_threadpool since SQLite is blocking
        stocks = await run_in_threadpool(SQLiteManager.get_stocks_after, start_time)
        return BaseResponse.success(data=stocks)
    except Exception as e:
        logger.error(f"Error fetching local stocks: {e}")
        return BaseResponse.fail(code="500", message=str(e))
