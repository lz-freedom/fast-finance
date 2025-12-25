import asyncio
from fastapi import APIRouter, HTTPException, Query
from fastapi.concurrency import run_in_threadpool
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
from app.services.yahoo_service import YahooService
from app.services.investing_service import InvestingService
from app.core.constants import get_exchange_info_by_acronym, get_stock_info, PLATFORM_YAHOO, PLATFORM_INVESTING
import logging

router = APIRouter()
logger = logging.getLogger("fastapi")

class AggregatedDataResponse(BaseModel):
    info: Dict[str, Any]
    balance_yearly_yefinancials: Dict[str, Any]
    balance_quarterly_yefinancials: Dict[str, Any]
    income_yearly_yefinancials: Dict[str, Any]
    income_quarterly_yefinancials: Dict[str, Any]
    cashflow_yearly_yefinancials: Dict[str, Any]
    cashflow_quarterly_yefinancials: Dict[str, Any]
    news: List[Dict[str, Any]]
    splits: List[Dict[str, Any]]
    dividends: List[Dict[str, Any]]
    name_and_new_translations: Dict[str, Any]

class StockFinancialDataAggregationReq(BaseModel):
    stock_symbol: str = Query(..., description="股票代码")
    exchange_acronym: str = Query(..., description="交易所缩写 (例如 SZSE)")

@router.post("/stock_financial_data_aggregation", response_model=AggregatedDataResponse, summary="一次性并发获取所有AI需要股票数据")
async def stock_financial_data_aggregation(
    req: StockFinancialDataAggregationReq
):
    # 1. 获取平台信息
    yahoo_info = get_stock_info(req.stock_symbol, req.exchange_acronym, PLATFORM_YAHOO)
    investing_info = get_stock_info(req.stock_symbol, req.exchange_acronym, PLATFORM_INVESTING)
    
    if not yahoo_info or not investing_info:
        raise HTTPException(status_code=400, detail=f"Exchange acronym '{req.exchange_acronym}' not supported")

    yahoo_symbol = yahoo_info["stock_symbol"]
    
    # 3. 定义辅助任务处理程序（包装以抑制错误）
    async def fetch_yahoo_info():
        try:
            return await run_in_threadpool(YahooService.get_ticker_info, yahoo_symbol)
        except Exception as e:
            logger.error(f"Error fetching info: {e}")
            return {}

    async def fetch_financials(type_: str, freq: str):
        try:
            return await run_in_threadpool(YahooService.get_financials, yahoo_symbol, type_, freq)
        except Exception as e:
            logger.error(f"Error fetching financials {type_} {freq}: {e}")
            return {}

    async def fetch_news():
        try:
            return await run_in_threadpool(YahooService.get_news, yahoo_symbol)
        except Exception as e:
            logger.error(f"Error fetching news: {e}")
            return []

    async def fetch_splits():
        try:
            return await run_in_threadpool(YahooService.get_splits, yahoo_symbol)
        except Exception as e:
            logger.error(f"Error fetching splits: {e}")
            return []

    async def fetch_dividends():
        try:
            return await run_in_threadpool(YahooService.get_dividends, yahoo_symbol)
        except Exception as e:
            logger.error(f"Error fetching dividends: {e}")
            return []

    async def fetch_translations():
        country_code = investing_info["country_code"]
        investing_code = investing_info["exchange_code"]
        try:
            translations = await run_in_threadpool(InvestingService.get_translations, req.stock_symbol, [country_code])
            # 过滤逻辑
            filtered_quotes = []
            if "quotes" in translations and isinstance(translations["quotes"], list):
                for quote in translations["quotes"]:
                    q_exchange = quote.get("exchange", "")
                    q_symbol = quote.get("symbol", "")
                    
                    if investing_code.lower() in q_exchange.lower() and req.stock_symbol.lower() == q_symbol.lower():
                         filtered_quotes.append(quote)
            
            translations["quotes"] = filtered_quotes
            return translations
        except Exception as e:
            logger.error(f"Error fetching Investing data: {e}")
            return {"quotes": [], "news": [], "articles": []}

    # 4. 运行并发任务
    # 使用 gather 保证所有任务运行。异常在任务内部处理。
    results = await asyncio.gather(
        fetch_yahoo_info(),
        fetch_financials("balance", "yearly"),
        fetch_financials("balance", "quarterly"),
        fetch_financials("income", "yearly"),
        fetch_financials("income", "quarterly"),
        fetch_financials("cashflow", "yearly"),
        fetch_financials("cashflow", "quarterly"),
        fetch_news(),
        fetch_splits(),
        fetch_dividends(),
        fetch_translations()
    )

    # Unpack Results
    (
        info,
        balance_yearly,
        balance_quarterly,
        income_yearly,
        income_quarterly,
        cashflow_yearly,
        cashflow_quarterly,
        news,
        splits,
        dividends,
        translations
    ) = results

    # 5. 检查是否有数据返回
    # 规则："以下项任意一个有值接口都返回成功"
    # 我们检查是否有任何主要字典/列表非空
    has_data = any([
        info,
        balance_yearly,
        balance_quarterly,
        income_yearly,
        income_quarterly,
        cashflow_yearly,
        cashflow_quarterly,
        news,
        splits,
        dividends,
        # 对于翻译数据，检查是否有内容
        translations.get("quotes") or translations.get("news") or translations.get("articles")
    ])

    if not has_data:
        # 如果完全没有返回任何内容，则抛出异常
        # 给定“任意一个有值即成功”，反之“无值即失败”是合理的。
        raise HTTPException(status_code=404, detail="No data found for the given symbol and exchange on any platform")

    return {
        "info": info,
        "balance_yearly_yefinancials": balance_yearly,
        "balance_quarterly_yefinancials": balance_quarterly,
        "income_yearly_yefinancials": income_yearly,
        "income_quarterly_yefinancials": income_quarterly,
        "cashflow_yearly_yefinancials": cashflow_yearly,
        "cashflow_quarterly_yefinancials": cashflow_quarterly,
        "news": news,
        "splits": splits,
        "dividends": dividends,
        "name_and_new_translations": translations
    }
