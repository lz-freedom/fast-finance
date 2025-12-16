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
    YahooCalendarRequest
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
        data = YahooService.get_financials(request.symbol, request.type.value)
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
