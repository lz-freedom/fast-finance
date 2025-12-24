import yfinance as yf
import pandas as pd
from typing import List, Dict, Any, Optional
import json
import logging
import requests
from requests.exceptions import HTTPError
import platformdirs as _ad
import os
from app.core.utils import recursive_camel_case
from app.core.config import settings

logger = logging.getLogger("fastapi")

# --- Yahoo Finance Configuration ---
# Enable debug mode for deeper insights
# yf.enable_debug_mode()

# Configure Cache Location
# Use a dedicated cache directory within the project root
CACHE_DIR = os.path.join(os.getcwd(), ".yfinance-cache")
if not os.path.exists(CACHE_DIR):
    os.makedirs(CACHE_DIR, exist_ok=True)

try:
    # yf.set_tz_cache_location(CACHE_DIR)
    logger.info(f"yfinance cache location set to: {CACHE_DIR}")
except Exception as e:
    logger.warning(f"Failed to set yfinance cache location: {e}")

# Apply Proxy Configuration
if settings.PROXY_YAHOO:
    try:
        # Must be a dict for yfinance/curl_cffi
        proxy_url = settings.PROXY_YAHOO
        yf.config.network.proxy = {"http": proxy_url, "https": proxy_url}
        yf.config.network.retries = 3
        logger.info(f"yfinance proxy set to: {settings.PROXY_YAHOO}")
    except Exception as e:
        logger.error(f"Failed to set yfinance proxy: {e}")

class YahooService:
    @staticmethod
    def _safe_dataframe_to_dict(df: Any, orientation: str = "records") -> Any:
        try:
            if df is None:
                return None
            if isinstance(df, pd.DataFrame):
                if df.empty:
                    return [] if orientation == "records" else {}
                # Handle timestamps/NaNs
                df = df.where(pd.notnull(df), None)
                # Convert timestamps to strings if any
                return json.loads(df.to_json(orient=orientation, date_format="iso"))
            return df
        except Exception as e:
            logger.warning(f"Error converting DataFrame: {e}")
            return None

    @staticmethod
    def get_ticker_info(symbol: str) -> Dict[str, Any]:
        try:
            ticker = yf.Ticker(symbol)
            return recursive_camel_case(ticker.info)
        except (json.JSONDecodeError, HTTPError) as e:
            logger.error(f"Yahoo API Error (Rate Limit/Block) for {symbol}: {e}")
            raise Exception(f"Yahoo Finance API blocked request (429/403): {str(e)}")
        except Exception as e:
            logger.error(f"Error fetching info for {symbol}: {e}")
            raise e

    @staticmethod
    def get_history(symbol: str, period: str, interval: str) -> List[Dict[str, Any]]:
        try:
            ticker = yf.Ticker(symbol)
            df = ticker.history(period=period, interval=interval)
            
            if df.empty:
                return []

            df.reset_index(inplace=True)
            date_col = 'Date' if 'Date' in df.columns else 'Datetime'
            
            result = []
            for _, row in df.iterrows():
                record = {
                    "date": row[date_col].isoformat() if hasattr(row[date_col], 'isoformat') else str(row[date_col]),
                    "open": row.get('Open') if pd.notna(row.get('Open')) else None,
                    "high": row.get('High') if pd.notna(row.get('High')) else None,
                    "low": row.get('Low') if pd.notna(row.get('Low')) else None,
                    "close": row.get('Close') if pd.notna(row.get('Close')) else None,
                    "volume": int(row.get('Volume')) if pd.notna(row.get('Volume')) else 0
                }
                result.append(record)
            
            # recursive_camel_case is generic, but get_history manually constructs dicts with consistent keys,
            # so we only apply it if keys like "Adj Close" might appear, but here we manually map.
            # Keeping manual map is safer for standard K-line format, maybe skip recursive_camel_case here 
            # or apply it if we used to_dict(). Manual mapping above uses "open", "close" etc which are already good.
            return result
        except Exception as e:
            logger.error(f"Error fetching history for {symbol}: {e}")
            raise e

    @staticmethod
    def get_financials(symbol: str, type_: str, freq: str = "yearly") -> Dict[str, Any]:
        try:
            ticker = yf.Ticker(symbol)
            df = pd.DataFrame()
            
            # Use method calls with freq parameter instead of properties
            if type_ == "balance":
                df = ticker.get_balance_sheet(freq=freq)
            elif type_ == "income":
                df = ticker.get_income_stmt(freq=freq)
            elif type_ == "cashflow":
                df = ticker.get_cashflow(freq=freq)
            
            if df.empty:
                return {}

            df = df.where(pd.notnull(df), None)
            df.columns = [col.strftime('%Y-%m-%d') if hasattr(col, 'strftime') else str(col) for col in df.columns]
            # Convert the raw dict keys (like "Total Assets") to camelCase
            return recursive_camel_case(df.to_dict())
        except Exception as e:
            logger.error(f"Error fetching financials for {symbol}: {e}")
            raise e

    @staticmethod
    def search_tickers(query: str) -> List[Dict[str, Any]]:
        # Search results are manually constructed, keys are already safe.
        try:
            search = yf.Search(query, news_count=0)
            results = search.quotes
            cleaned_results = []
            for item in results:
                if item.get('quoteType') == 'EQUITY':
                    cleaned_results.append({
                        "symbol": item.get('symbol'),
                        "shortname": item.get('shortname'),
                        "longname": item.get('longname'),
                        "exchange": item.get('exchange'),
                        "type": item.get('quoteType')
                    })
            return cleaned_results
        except Exception as e:
            logger.error(f"Error searching for {query}: {e}")
            return []

    # --- New Methods ---

    @staticmethod
    def get_news(symbol: str) -> List[Dict[str, Any]]:
        try:
            ticker = yf.Ticker(symbol)
            news = ticker.news
            if not news:
                return []
            return recursive_camel_case(news)
        except Exception as e:
            logger.error(f"Error fetching news for {symbol}: {e}")
            return [] 

    @staticmethod
    def get_holders(symbol: str) -> Dict[str, Any]:
        try:
            ticker = yf.Ticker(symbol)
            
            major = YahooService._safe_dataframe_to_dict(ticker.major_holders, orientation="records")
            inst = YahooService._safe_dataframe_to_dict(ticker.institutional_holders, orientation="records")
            mutual = YahooService._safe_dataframe_to_dict(ticker.mutualfund_holders, orientation="records")
            
            return recursive_camel_case({
                "major_holders": major,
                "institutional_holders": inst,
                "mutualfund_holders": mutual
            })
        except Exception as e:
            logger.error(f"Error fetching holders for {symbol}: {e}")
            return {}

    @staticmethod
    def get_analysis(symbol: str) -> Dict[str, Any]:
        try:
            ticker = yf.Ticker(symbol)
            
            rec = YahooService._safe_dataframe_to_dict(ticker.recommendations)
            rec_sum = YahooService._safe_dataframe_to_dict(ticker.recommendations_summary)
            up_down = YahooService._safe_dataframe_to_dict(ticker.upgrades_downgrades)

            target_mean = None
            if ticker.info:
                target_mean = ticker.info.get("targetMeanPrice")

            return recursive_camel_case({
                "recommendations": rec,
                "recommendations_summary": rec_sum,
                "target_mean": target_mean,
                "upgrades_downgrades": up_down
            })
        except Exception as e:
            logger.error(f"Error fetching analysis for {symbol}: {e}")
            return {}

    @staticmethod
    def get_calendar(symbol: str) -> Dict[str, Any]:
        try:
            ticker = yf.Ticker(symbol)
            cal = ticker.calendar
            
            if isinstance(cal, pd.DataFrame):
                 return recursive_camel_case(YahooService._safe_dataframe_to_dict(cal))
            
            return recursive_camel_case({"calendar": cal})
        except Exception as e:
            logger.error(f"Error fetching calendar for {symbol}: {e}")
            return {}

    @staticmethod
    def get_splits(symbol: str, period: str = "max") -> List[Dict[str, Any]]:
        try:
            ticker = yf.Ticker(symbol)
            # get_splits returns a Series with Date index and Split Ratio values
            splits = ticker.get_splits(period=period)
            
            if splits.empty:
                return []
            
            # Convert Series to list of dicts
            # Series index is Date (Timestamp), value is Float (Split Ratio)
            result = []
            for date, ratio in splits.items():
                 result.append({
                     "date": date.isoformat() if hasattr(date, 'isoformat') else str(date),
                     "ratio": ratio
                 })
            # Descending order by date usually better for display
            result.sort(key=lambda x: x['date'], reverse=True)
            return result
        except Exception as e:
             logger.error(f"Error fetching splits for {symbol}: {e}")
             return []

    @staticmethod
    def get_dividends(symbol: str, period: str = "max") -> List[Dict[str, Any]]:
        try:
            ticker = yf.Ticker(symbol)
            # get_dividends returns a Series with Date index and Dividend Amount values
            dividends = ticker.get_dividends(period=period)
            
            if dividends.empty:
                return []
            
            result = []
            for date, amount in dividends.items():
                 result.append({
                     "date": date.isoformat() if hasattr(date, 'isoformat') else str(date),
                     "amount": amount
                 })
            result.sort(key=lambda x: x['date'], reverse=True)
            return result
        except Exception as e:
             logger.error(f"Error fetching dividends for {symbol}: {e}")
             return []


    @staticmethod
    def get_active_stocks(
        regions: List[str],
        min_intraday_market_cap: int,
        min_day_volume: int,
        exchanges: List[str],
        size: int
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Get most active stocks by region using Yahoo Finance Screener API.
        Uses yfinance.EquityQuery and yf.screen.
        """
        data = {}
        
        for region in regions:
            try:
                query = EquityQuery("and", [
                    EquityQuery("eq", ["region", region]),
                    EquityQuery("gte", ["intradaymarketcap", min_intraday_market_cap]),
                    EquityQuery("gt", ["dayvolume", min_day_volume]),
                    EquityQuery("is-in", ['exchange', *exchanges])
                ])
                
                resp = yf.screen(
                    query,
                    size=size,
                    sortField="dayvolume",
                    sortAsc=False
                )
                
                # resp["quotes"] contains the list of stocks
                quotes = resp.get("quotes", [])
                
                cleaned_list = []
                for q in quotes:
                    cleaned_list.append(recursive_camel_case(q))
                    
                data[region] = cleaned_list
                logger.info(f"Fetched {len(cleaned_list)} stocks for region {region}")
                
            except Exception as e:
                logger.error(f"Error fetching screener for region {region}: {e}")
                data[region] = []
        
        return data
