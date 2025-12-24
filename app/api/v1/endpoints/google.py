from fastapi import APIRouter
from typing import List, Dict, Any
from app.services.google_service import GoogleService
from app.schemas.response import BaseResponse
from app.schemas.google import (
    GoogleSearchRequest, GoogleSearchResponse,
    GoogleDetailRequest, GoogleDetailResponse,
    GoogleDetailsRequest,
    GoogleHistoryRequest, GoogleHistoryResponse
)

router = APIRouter()

@router.post("/search", response_model=BaseResponse, summary="Google Finance 搜索股票")
async def search(request: GoogleSearchRequest):
    """
    搜索股票，返回匹配的代码、交易所和名称。
    """
    try:
        results = GoogleService.search(request.query)
        # Map raw dicts to Response Model manually or let Pydantic handle it if keys match
        # GoogleService returns dicts with 'symbol', 'exchange', 'name' etc.
        # Ensure 'code' maps to 'symbol' or update schema
        
        # Schema uses 'code', Service returns 'symbol'. Mapping needed.
        mapped_results = []
        for item in results:
            if item:
                mapped_results.append({
                    "code": item.get("symbol"),
                    "exchange": item.get("exchange"),
                    "name": item.get("name"),
                    "type": None, # Not parsed currently
                    "region": item.get("region")
                })
        
        return BaseResponse.success(data=mapped_results)
    except Exception as e:
        raise e

@router.post("/detail", response_model=BaseResponse, summary="获取单个股票详情")
async def get_detail(request: GoogleDetailRequest):
    """
    获取单个股票的实时行情数据。
    """
    try:
        data = GoogleService.get_detail(request.symbol, request.exchange)
        # Service returns 'symbol', Schema uses 'code'.
        if data:
            data['code'] = data.pop('symbol', None)
        return BaseResponse.success(data=data)
    except Exception as e:
        raise e

@router.post("/details", response_model=BaseResponse, summary="批量获取股票详情")
async def get_details(request: GoogleDetailsRequest):
    """
    批量获取多个股票的行情数据。
    """
    try:
        # Convert Pydantic models to dict list
        items = [{"symbol": item.symbol, "exchange": item.exchange} for item in request.symbols]
        results = GoogleService.get_details(items)
        
        mapped_results = []
        for data in results:
            if data:
                data['code'] = data.pop('symbol', None)
                mapped_results.append(data)
            else:
                mapped_results.append(None)
                
        return BaseResponse.success(data=mapped_results)
    except Exception as e:
        raise e

@router.post("/history", response_model=BaseResponse, summary="获取股票历史数据")
async def get_history(request: GoogleHistoryRequest):
    """
    获取股票历史K线数据 (Simple Format: Date, Close, Volume)。
    """
    try:
        data = GoogleService.get_history(request.symbol, request.exchange, request.range.value)
        return BaseResponse.success(data={
            "symbol": request.symbol,
            "exchange": request.exchange,
            "range": request.range.value,
            "data": data
        })
    except Exception as e:
        raise e
