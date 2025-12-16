from fastapi import APIRouter, HTTPException
from app.services.tradingview.core import TA_Handler, TradingView, get_multiple_analysis
from app.schemas.response import BaseResponse
from app.schemas.tradingview import AnalysisRequest, MultipleAnalysisRequest, SearchRequest
import logging

router = APIRouter()

@router.post("/analysis", response_model=BaseResponse, summary="单标的技术分析")
async def get_analysis(request: AnalysisRequest):
    """
    获取单个交易标的的详细技术分析数据 (Summary, Oscillators, Moving Averages, Indicators)
    """
    try:
        handler = TA_Handler(
            symbol=request.symbol,
            exchange=request.exchange,
            screener=request.screener.value, # Enum value
            interval=request.interval.value
        )
        analysis = handler.get_analysis()
        
        data = {
            "symbol": analysis.symbol,
            "exchange": analysis.exchange,
            "screener": analysis.screener,
            "interval": analysis.interval,
            "time": analysis.time,
            "summary": analysis.summary,
            "oscillators": analysis.oscillators,
            "moving_averages": analysis.moving_averages,
            "indicators": analysis.indicators
        }
        return BaseResponse.success(data=data)
    except Exception as e:
        import traceback
        logging.error(f"TradingView Analysis Error: {e}\n{traceback.format_exc()}")
        raise e # Let global handler process it

@router.post("/analysis/multiple", response_model=BaseResponse, summary="批量技术分析")
async def get_analysis_multiple(request: MultipleAnalysisRequest):
    """
    获取多个标的的技术分析数据。
    """
    try:
        results = get_multiple_analysis(
            symbols=request.symbols,
            screener=request.screener.value,
            interval=request.interval.value
        )
        
        serialized_results = {}
        for key, analysis in results.items():
            if analysis:
                serialized_results[key] = {
                    "summary": analysis.summary,
                    "oscillators": analysis.oscillators,
                    "moving_averages": analysis.moving_averages,
                    "indicators": analysis.indicators,
                    "time": analysis.time
                }
            else:
                serialized_results[key] = None
                
        return BaseResponse.success(data=serialized_results)
    except Exception as e:
        import traceback
        logging.error(f"TradingView Multiple Analysis Error: {e}\n{traceback.format_exc()}")
        raise e

@router.post("/search", response_model=BaseResponse, summary="搜索标的")
async def search_symbols(request: SearchRequest):
    """
    搜索交易标的，返回 Symbol, Exchange, Type 等信息。
    """
    try:
        results = TradingView.search(request.text, request.type)
        return BaseResponse.success(data=results)
    except Exception as e:
        raise e
