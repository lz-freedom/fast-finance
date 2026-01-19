import yfinance as yf


import pandas as pd
from typing import List, Dict, Any, Optional, Union
from datetime import date, datetime, timedelta
import threading
from dateutil.relativedelta import relativedelta
import numpy as np
import json
import logging
import requests
from requests.exceptions import HTTPError
import platformdirs as _ad
import os
from app.core.utils import recursive_camel_case, to_camel_case
from app.core.config import settings
from app.core.constants import get_stock_info, PLATFORM_YAHOO
from app.core.database import DBManager
from io import StringIO

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
    
yf.config.debug.logging = True
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

# Simple in-memory cache removed. Using DBManager.

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
    def _sanitize_value(val: Any) -> Any:
        """
        Recursively sanitizes values to ensure they are JSON compliant.
        - Converts NaN, Infinity, -Infinity to None.
        - Converts numpy types to native python types.
        """
        if isinstance(val, float):
            if np.isnan(val) or np.isinf(val):
                return None
            return val
        elif isinstance(val, (np.integer, np.int64, np.int32)):
            return int(val)
        elif isinstance(val, (np.floating, np.float64, np.float32)):
            if np.isnan(val) or np.isinf(val):
                return None
            return float(val)
        elif isinstance(val, dict):
            return {k: YahooService._sanitize_value(v) for k, v in val.items()}
        elif isinstance(val, list):
            return [YahooService._sanitize_value(v) for v in val]
        return val

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
    def get_stock_latest_price(symbol: str) -> Dict[str, Any]:
        """
        查询单只股票最新常规市场价格 (Price, Change, Time).
        Use ticker.info as fast_info lacks regularMarketTime.
        """
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            return {
                "stock_symbol": info.get("symbol"),
                "current_price": info.get("currentPrice"),
                "change_amount": info.get("regularMarketChange"),
                "change_percent": info.get("regularMarketChangePercent"),
                "regular_market_time": info.get("regularMarketTime"),
                "exchange_timezone_short_name": info.get("exchangeTimezoneShortName")
            }
        except Exception as e:
            logger.error(f"Error fetching latest price for {symbol}: {e}")
            raise e

    @staticmethod
    def get_history(symbol: str, period: str, interval: str, auto_adjust: bool = False, repair: bool = True) -> List[Dict[str, Any]]:
        try:
            ticker = yf.Ticker(symbol)
            df = ticker.history(period=period, interval=interval, auto_adjust=auto_adjust, repair=repair)
            
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
                    "adj_close": row.get('Adj Close') if pd.notna(row.get('Adj Close')) else None,
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
    def get_financials(symbol: str, type_: str, freq: str = "yearly") -> List[Dict[str, Any]]:
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
                return []

            df = df.where(pd.notnull(df), None)
            
            results = []
            # Calculate camelCase mapping once for all rows
            index_map = {idx: to_camel_case(str(idx)) for idx in df.index}
            
            for col_name in df.columns:
                date_str = col_name.strftime('%Y-%m-%d') if hasattr(col_name, 'strftime') else str(col_name)
                
                # Create base object with date
                item = {"date": date_str}
                
                # Add metrics
                for idx, val in df[col_name].items():
                    key = index_map.get(idx, str(idx))
                    item[key] = val
                    
                results.append(item)
                
            return results
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
                from yfinance import EquityQuery
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

    @staticmethod
    def get_related_stock(stock_symbol: str, exchange_acronym: str) -> Dict[str, Any]:
        """
        Get related stock information (Compare To, People Also Watch).
        Uses caching and enrichment from yahoo_stock table.
        """
        # 1. Construct Yahoo Symbol
        from app.core.constants import get_stock_info, PLATFORM_YAHOO
        info = get_stock_info(stock_symbol, exchange_acronym, PLATFORM_YAHOO)
        yahoo_symbol = info["stock_symbol"] if info else stock_symbol

        # 2. Check Cache
        cached = DBManager.get_yahoo_stock_related_cache(yahoo_symbol)
        
        data = None
        current_time = datetime.now()
        should_update = False
        
        if cached:
            try:
                data = json.loads(cached["data"])
                cache_time = cached["created_at"]
                if isinstance(cache_time, str):
                    try:
                        cache_time = datetime.fromisoformat(cache_time)
                    except:
                        pass
                
                if isinstance(cache_time, datetime):
                    if (current_time - cache_time) > timedelta(days=1):
                        should_update = True
                else:
                    should_update = True
            except Exception as e:
                logger.error(f"Error parsing cache for {yahoo_symbol}: {e}")
                should_update = True
        else:
            should_update = True
            
        # 3. Fallback / Update Logic
        if not data:
            data = YahooService.web_crawler(yahoo_symbol)
            if data:
                DBManager.upsert_yahoo_stock_related_cache(yahoo_symbol, json.dumps(data))
        elif should_update:
            threading.Thread(target=YahooService._background_update_related, args=(yahoo_symbol,)).start()

        if not data:
            return {
                "compare_to_list": [],
                "people_also_watch_list": []
            }

        # 4. Enrichment
        return YahooService._enrich_related_data(data)

    @staticmethod
    def _enrich_related_data(raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enrich raw crawler data using yahoo_stock table.
        Discard items not found in DB.
        """
        compare_list = raw_data.get("compare_to", [])
        watch_list = raw_data.get("people_also_watch", [])
        
        # Helper to extract symbol from raw item
        def extract_sym(item):
            return item.get("symbol") # usage of 'symbol' matches scraper output

        all_yahoo_symbols = []
        for item in compare_list:
            s = extract_sym(item)
            if s: all_yahoo_symbols.append(s)
        for item in watch_list:
            s = extract_sym(item)
            if s: all_yahoo_symbols.append(s)
            
        if not all_yahoo_symbols:
            return {
                "compare_to_list": [],
                "people_also_watch_list": []
            }

        db_map = DBManager.get_yahoo_stock_by_symbols(all_yahoo_symbols)
        
        enriched_compare = []
        enriched_watch = []
        
        def process_list(src_list, dest_list):
            for item in src_list:
                ys = extract_sym(item)
                if not ys: continue
                
                db_info = db_map.get(ys)
                if db_info:
                    data_item = {
                        "stock_symbol": db_info["stock_symbol"],
                        "exchange_acronym": db_info["exchange_acronym"],
                        "name": db_info["name"]
                    }
                    if item.get("currentPrice") is not None:
                        data_item["currentPrice"] = item.get("currentPrice")
                    dest_list.append(data_item)
                # Else discard
                    
        process_list(compare_list, enriched_compare)
        process_list(watch_list, enriched_watch)
        
        return {
            "compare_to_list": enriched_compare,
            "people_also_watch_list": enriched_watch
        }

    @staticmethod
    def web_crawler(symbol: str) -> Dict[str, Any]:
        """
        Scrapes raw analysis data from Yahoo Finance web page.
        """
        return YahooService._scrape_analysis_from_web(symbol)
    
    @staticmethod
    def _background_update_related(symbol: str):
        try:
            new_data = YahooService._scrape_analysis_from_web(symbol)
            if new_data:
                DBManager.upsert_yahoo_stock_related_cache(symbol, json.dumps(new_data))
        except Exception as e:
            logger.error(f"Background update failed for {symbol}: {e}")

    @staticmethod
    def _scrape_analysis_from_web(symbol: str) -> Dict[str, Any]:
        url = f"https://finance.yahoo.com/quote/{symbol}/"
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5"
        }
        
        try:
            resp = requests.get(url, headers=headers, timeout=10)
            if resp.status_code != 200:
                logger.error(f"Failed to scrape Yahoo page for {symbol}: {resp.status_code}")
                return {}
            
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(resp.text, "html.parser")
            
            result = {
                "returns": {},
                "compare_to": [],
                "people_also_watch": []
            }
            
            # Helper to extract signed text
            def get_signed_text(el):
                if not el: return ""
                text = el.get_text(strip=True)
                if not text: return ""
                
                # Check for explicit negative class
                is_negative = False
                if el.has_attr("class"):
                    classes = el["class"]
                    for c in classes:
                        c_lower = c.lower()
                        if "negative" in c_lower or "neg" in c_lower or "down" in c_lower or "red" in c_lower:
                            is_negative = True
                            break
                            
                # If text already has sign, trust it
                if text.startswith("+") or text.startswith("-"):
                    return text
                    
                if is_negative and not text.startswith("-"):
                    return f"-{text}"
                return text
            
            # 1. Performance Overview
            perf_section = soup.find("section", {"data-testid": "performance-overview"})
            if perf_section:
                cards = perf_section.find_all("section", {"data-testid": "card-container"})
                for card in cards:
                    title_div = card.find("h3", class_="title")
                    if not title_div: continue
                    title_text = title_div.get_text(strip=True)
                    
                    key = None
                    if "YTD" in title_text: key = "YTD"
                    elif "1-Year" in title_text: key = "1-Year"
                    elif "3-Year" in title_text: key = "3-Year"
                    elif "5-Year" in title_text: key = "5-Year"
                    
                    if key:
                        info_div = card.find("div", class_=lambda x: x and "perfInfo" in x)
                        if info_div:
                            rows = info_div.find_all("div", recursive=False)
                            if len(rows) >= 2:
                                stock_perf = rows[0].find("div", class_=lambda x: x and "perf" in x)
                                index_row = rows[1]
                                index_perf = index_row.find("div", class_=lambda x: x and "perf" in x)
                                index_symbol = index_row.find("div", class_=lambda x: x and "symbol" in x)
                                
                                result["returns"][key] = {
                                    "stock": get_signed_text(stock_perf),
                                    "index": get_signed_text(index_perf),
                                    "index_name": index_symbol.get_text(strip=True) if index_symbol else ""
                                }
                            elif len(rows) == 1:
                                stock_perf = rows[0].find("div", class_=lambda x: x and "perf" in x)
                                result["returns"][key] = {
                                    "stock": get_signed_text(stock_perf),
                                    "index": None,
                                    "index_name": None
                                }

            # Helper for tickers
            def extract_tickers(section_testid, result_key):
                section = soup.find("section", {"data-testid": section_testid})
                if section:
                    cards = section.find_all("section", {"data-testid": "card-container"})
                    for card in cards:
                        price_val = None
                        
                        # Attempt 1: Compare To structure (span class="price ...")
                        price_span = card.find("span", class_=lambda x: x and "price" in x)
                        if price_span:
                            price_val = price_span.get_text(strip=True)
                        
                        # Attempt 2: People Also Watch (div.moreInfo span strong)
                        if not price_val:
                            more_info = card.find("div", class_=lambda x: x and "moreInfo" in x)
                            if more_info:
                                strong = more_info.find("strong")
                                if strong:
                                    price_val = strong.get_text(strip=True)
                        
                        # Attempt 3: fin-streamer (fallback)
                        if not price_val:
                            price_el = card.find("fin-streamer", {"data-field": "regularMarketPrice"})
                            if price_el:
                                price_val = price_el.get_text(strip=True)

                        # Parse Price
                        if price_val:
                             try:
                                 # Remove commas and handle weird chars
                                 price_val = price_val.replace(',', '')
                                 price_val = float(price_val)
                             except:
                                 price_val = None

                        # Strategy 1: Compare To (tickerContainer)
                        ticker_container = card.find("div", class_=lambda x: x and "tickerContainer" in x)
                        if ticker_container:
                            a = ticker_container.find("a")
                            if a:
                                s_el = a.find("span")
                                n_el = a.find("div", class_=lambda c: c and "longName" in c)
                                if s_el and n_el:
                                    s = s_el.get_text(strip=True)
                                    n = n_el.get_text(strip=True)
                                    if s and s != symbol:
                                        result[result_key].append({"symbol": s, "name": n, "price": price_val})
                                        continue

                        # Strategy 2: People Also Watch (generic structure)
                        # Structure seen: 
                        # <div class="ticker-container ..."> <span class="ticker-wrapper ..."> <div class="ticker ..."> <div class="name ..."> <span class="symbol ...">AMZN</span> <span class="longName ...">Amazon...</span>
                        
                        sym_span = card.find("span", class_=lambda x: x and "symbol" in x)
                        name_span = card.find(class_=lambda x: x and "longName" in x)
                        
                        if sym_span:
                            s = sym_span.get_text(strip=True)
                            n = name_span.get_text(strip=True) if name_span else ""
                            if not n and name_span and name_span.has_attr("title"):
                                n = name_span["title"]
                            
                            if s and s != symbol:
                                result[result_key].append({"symbol": s, "name": n, "price": price_val})

            extract_tickers("compare-to", "compare_to")
            extract_tickers("people-also-watch", "people_also_watch")

            # Dedup
            def dedup(l):
                seen = set()
                new_l = []
                for i in l:
                    if i["symbol"] not in seen:
                        seen.add(i["symbol"])
                        new_l.append(i)
                return new_l

            result["compare_to"] = dedup(result["compare_to"])
            result["people_also_watch"] = dedup(result["people_also_watch"])
            
            return result
            
        except Exception as e:
            logger.error(f"Error scraping Yahoo analysis for {symbol}: {e}")
            return {}

    @staticmethod
    def get_batch_basic_info(symbols: List[str]) -> Dict[str, Dict[str, Any]]:
        """
        Batch fetch basic info for a list of symbols to get exchange and price.
        Returns map: symbol -> {exchange: str, price: float}
        """
        if not symbols:
            return {}
            
        try:
            # yf.Tickers expects spac-separated string
            tickers_str = " ".join(symbols)
            tickers = yf.Tickers(tickers_str)
            
            result = {}
            for symbol in symbols:
                # Accessing tickers.tickers[symbol] is lazy, but accessing .fast_info triggers fetch
                # Note: yfinance might change case of symbol key if not found exactly? 
                # Usually it respects input case if valid.
                
                # Handle case where symbol might be transformed by yfinance (though usually it's fine)
                # We iterate our input symbols and try to access the ticker object
                
                try:
                    # Tickers dict keys are usually upper case
                    t = tickers.tickers.get(symbol.upper(), None)
                    if not t:
                        continue
                        
                    fast_info = t.fast_info
                    
                    # Exchange is often available in fast_info directly or via property
                    # fast_info keys: 'exchange', 'lastPrice', 'currency', ...
                    
                    exchange_code = fast_info.get('exchange')
                    last_price = fast_info.get('lastPrice')
                    
                    result[symbol] = {
                        "exchange": exchange_code,
                        "currentPrice": last_price
                    }
                except Exception as inner_e:
                    logger.warning(f"Failed to get fast_info for {symbol}: {inner_e}")
                    continue
                    
            return result
        except Exception as e:
            logger.error(f"Error batch fetching info for symbols: {e}")
            return {}

    @staticmethod
    def get_batch_stock_base_data(items: List[Dict[str, str]], is_return_history: bool = False) -> List[Dict[str, Any]]:
        """
        批量获取股票基础数据。
        :param items: List of dicts with keys "stock_symbol", "exchange_acronym"
        :param is_return_history: Whether to include historical k-line data in the response
        """
        if not items:
            return []

        # Prepare symbols for batch fetching
        # We need to resolve yahoo symbols first
        # map: yahoo_symbol -> {stock_symbol: ..., exchange_acronym: ...}
        yahoo_symbol_map = {}
        
        for item in items:
            raw_symbol = item.get("stock_symbol")
            acronym = item.get("exchange_acronym")
            
            if not raw_symbol or not acronym:
                continue
                
            info_map = get_stock_info(raw_symbol, acronym, PLATFORM_YAHOO)
            if info_map:
                y_sym = info_map["stock_symbol"]
                yahoo_symbol_map[y_sym] = {
                    "stock_symbol": raw_symbol,
                    "exchange_acronym": acronym,
                    "yahoo_symbol": y_sym
                }
        
        unique_yahoo_symbols = list(yahoo_symbol_map.keys())
        
        # Buffer days for history fetching to calculate returns
        BUFFER_DAYS = 35
        # Years for returns
        YEARS = (1, 3, 5)

        logger.info(f"Batch fetching base data for {len(unique_yahoo_symbols)} symbols")

        try:
            tickers = yf.Tickers(" ".join(unique_yahoo_symbols))
            results = []

            for y_sym in unique_yahoo_symbols:
                original_info = yahoo_symbol_map[y_sym]
                
                try:
                    # Access ticker
                    t = tickers.tickers[y_sym]
                    
                    
                    # 1. Fetch Info
                    info = t.info 
                    if info is None:
                        logger.warning(f"Info is None for {y_sym}")
                        info = {}

                    # Get Timezone early for cache correction
                    tz_name = info.get("exchangeTimezoneName")
                    
                    # --- Core Logic from User for Returns ---
                    market_state = info.get("marketState") or ""
                    # Normalize strings for comparison
                    ms_upper = str(market_state).upper()
                    use_today = ("REGULAR" in ms_upper) or ("POST" in ms_upper)
                    
                    # Short history for "latest trading day" check
                    hist_short = t.history(period="10d", interval="1d", auto_adjust=False, repair=True)
                    
                    if hist_short is None or hist_short.empty or "Adj Close" not in hist_short.columns:
                        logger.warning(f"No history found for {y_sym}")
                        # Even if no history, we try to return profile info? 
                        # User snippet continued with None for returns. behavior: append minimalist row
                        # But we want to return full profile if possible. 
                        # Let's proceed with defaults for returns fields.
                        last_hist_date = None
                        last_hist_adj = None
                        as_of_date = date.today()
                        end_price = None
                    else:
                        hist_short = hist_short.sort_index()
                        last_hist_dt = hist_short.index[-1]
                        last_hist_date = last_hist_dt.date()
                        last_hist_adj = float(hist_short.iloc[-1]["Adj Close"])
                        
                        if use_today:
                            end_price = info.get("currentPrice")
                            if end_price is None:
                                # Fallback or keep None
                                end_price = None
                            
                            tz = info.get("exchangeTimezoneName")
                            # If we can't determine current time from timezone, use UTC or server time?
                            # pd.Timestamp.now(tz=tz) is good
                            try:
                                as_of_date = pd.Timestamp.now(tz=tz).date() if tz else date.today()
                            except:
                                as_of_date = date.today()
                        else:
                            end_price = last_hist_adj
                            as_of_date = last_hist_date
                    
                    # --- Calculate Returns ---
                    # We need history for 5 years back from as_of_date
                    calculated_returns = {
                        "YTD": None, "3M": None, "6M": None, "1Y": None, "3Y": None, "5Y": None
                    }
                    calculated_ranges = {
                        "YTD": None, "3M": None, "6M": None, "1Y": None, "3Y": None, "5Y": None
                    }
                    
                    full_history_list = []
                    
                    # We always need history to calculate returns, even if is_return_history is False
                    if end_price is not None and as_of_date is not None:
                        # Construct Cache Key
                        # Key rules: Exchange Current Date + Yahoo Symbol + Market State
                        # as_of_date is derived from exchange timezone current time or close time, so it represents "Exchange Current Date" well enough for now
                        # However, user asked for "对应交易所的当前日期". as_of_date is exactly that (calculated above).
                        cache_key = f"{as_of_date}_{y_sym}_{market_state}"
                        
                        hist_long = None
                        
                        # Try DB Cache
                        cached_json = DBManager.get_history_cache(cache_key)
                        if cached_json:
                             logger.info(f"Cache hit for {cache_key}")
                             # Reconstruct DataFrame from JSON
                             # We use read_json with orient='split' or 'table' or 'records'. 
                             # 'index' orient is safer for time series if index is unique.
                             # Let's assume we saved with orient='index' or 'split'.
                             # For consistency with "Safe DataFrame" usually handling 'records', 
                             # but here we need the INDEX (Date) preserved.
                             
                             # Let's save/load with date_unit='ns' to preserve precision if possible
                             try:
                                 hist_long = pd.read_json(StringIO(cached_json), orient='index')
                                 # Ensure index is datetime
                                 hist_long.index = pd.to_datetime(hist_long.index)
                                 # Explicitly set index name, as read_json(orient='index') loses it
                                 hist_long.index.name = 'Date'
                                 
                                 # Fix Timezone: Cache saves as UTC ISO, which might shift the date (e.g. Shanghai +8)
                                 if tz_name:
                                     try:
                                         if hist_long.index.tz is None:
                                            # If naive (unlikely with ISO Z), localize to UTC first
                                            hist_long.index = hist_long.index.tz_localize("UTC")
                                         
                                         hist_long.index = hist_long.index.tz_convert(tz_name)
                                     except Exception as e:
                                         logger.warning(f"Failed to convert timezone for {y_sym}: {e}")
                             except Exception as e:
                                 logger.error(f"Failed to load cache: {e}")
                                 hist_long = None

                        if hist_long is None:
                             # Fetch deep history
                             start_date = as_of_date - relativedelta(years=5, days=BUFFER_DAYS)
                             end_date_query = as_of_date + relativedelta(days=1)
                             hist_long = t.history(start=start_date, end=end_date_query, interval="1d", auto_adjust=False)
                             
                             # Save to Cache
                             if not hist_long.empty:
                                 try:
                                     # Convert to JSON string (orient='index' preserves Date index)
                                     # date_format='iso' makes it readable and portable
                                     json_str = hist_long.to_json(orient='index', date_format='iso')
                                     DBManager.upsert_history_cache(cache_key, json_str)
                                 except Exception as e:
                                     logger.error(f"Failed to save cache: {e}")
                        
                        if hist_long is not None and not hist_long.empty and "Adj Close" in hist_long.columns:
                             hist_long = hist_long.sort_index()
                             
                             # Helper function
                             def get_adj_prev(anchor: date):
                                 sub = hist_long[hist_long.index.date <= anchor]
                                 if sub.empty:
                                     return None, None
                                 row = sub.iloc[-1]
                                 return float(row["Adj Close"]), row.name.date()

                             # YTD
                             ytd_anchor = date(as_of_date.year - 1, 12, 31)
                             p0, p0_date = get_adj_prev(ytd_anchor)
                             if p0:
                                 calculated_returns["YTD"] = (end_price / p0) - 1
                                 if p0_date:
                                     calculated_ranges["YTD"] = f"{p0_date.isoformat()}:{as_of_date.isoformat()}"

                             # Periods
                             periods = {
                                 "3M": relativedelta(months=3),
                                 "6M": relativedelta(months=6),
                                 "1Y": relativedelta(years=1),
                                 "3Y": relativedelta(years=3),
                                 "5Y": relativedelta(years=5)
                             }
                             
                             for key, delta in periods.items():
                                 anchor = as_of_date - delta
                                 p0, p0_date = get_adj_prev(anchor)
                                 if p0:
                                     calculated_returns[key] = (end_price / p0) - 1
                                     if p0_date:
                                         calculated_ranges[key] = f"{p0_date.isoformat()}:{as_of_date.isoformat()}"
                             
                             # Format History for Response (Last 5 Years)
                             # Filter hist_long to only include records within true 5y window
                             # User asked for "近5年每个交易日..."
                             if is_return_history:
                                 cutoff = as_of_date - relativedelta(years=5)
                                 hist_final = hist_long[hist_long.index.date >= cutoff]
                                 
                                 # Reset index to access Date
                                 hist_final = hist_final.reset_index()
                                 
                                 # Robust Date Column Detection
                                 date_col = 'Date'
                                 if 'Date' not in hist_final.columns:
                                     if 'Datetime' in hist_final.columns:
                                         date_col = 'Datetime'
                                     elif 'index' in hist_final.columns:
                                         date_col = 'index'
                                     else:
                                         # Fallback: take first column if likely a date?
                                         # For now, stick to safe knowns.
                                         # If we set index.name='Date' above, reset_index gives 'Date'.
                                         pass 
                                 
                                 for _, row in hist_final.iterrows():
                                      # Ensure date is a datetime object or Timestamp
                                      dt_val = row[date_col]
                                      
                                      # Default values
                                      date_raw = str(dt_val)
                                      date_fmt = str(dt_val)
                                      date_ts = 0
                                      
                                      if hasattr(dt_val, 'isoformat'):
                                          date_raw = dt_val.isoformat()
                                      
                                      if hasattr(dt_val, 'strftime'):
                                          date_fmt = dt_val.strftime('%Y-%m-%d')
                                          
                                      if hasattr(dt_val, 'timestamp'):
                                          date_ts = int(dt_val.timestamp())
                                      
                                      full_history_list.append({
                                          "date_raw": date_raw,
                                          "date": date_fmt,
                                          "date_timestamp": date_ts,
                                          "open": row.get('Open'),
                                          "high": row.get('High'),
                                          "low": row.get('Low'),
                                          "close": row.get('Close'),
                                          "adj_close": row.get('Adj Close'),
                                          "volume": row.get('Volume')
                                      })
                                     
                                 # Reverse Sort (Newest first)
                                 full_history_list.sort(key=lambda x: x['date'], reverse=True)

                    # --- Construct Response Item ---
                    # Helper safe get
                    def g(k, default=None):
                        return info.get(k, default)

                    # Company Officers
                    officers_raw = g("companyOfficers", [])
                    ceo_info = None
                    for off in officers_raw:
                        title = str(off.get('title', '')).lower()
                        if 'ceo' in title or 'chief executive officer' in title:
                            ceo_info = {
                                "name": off.get('name'),
                                "age": off.get('age'),
                                "birth_year": off.get('yearBorn'),
                                "total_pay": off.get('totalPay')
                            }
                            break
                    # If no CEO found, maybe take the first one or leave None? 
                    # Let's leave None if not sure.

                    # Sanitize and build
                    # Note: We rely on recursive_camel_case or manual mapping?
                    # The user provided a strict mapping list. We should follow it.
                    
                    # Name logic: displayName -> shortName -> longName
                    name_val = g("displayName")
                    if not name_val:
                        name_val = g("shortName")
                    if not name_val:
                        name_val = g("longName")
                        
                    item_data = {
                        "symbol": original_info["stock_symbol"],
                        "exchange_acronym": original_info["exchange_acronym"],
                        "yahoo_symbol": y_sym,
                        "yahoo_exchange": g("exchange"),
                        
                        # New Fields
                        "name": name_val,
                        "exchange_timezone_name": g("exchangeTimezoneName"),
                        "exchange_timezone_short_name": g("exchangeTimezoneShortName"),
                        "gmt_off_set_milliseconds": g("gmtOffSetMilliseconds"),
                        "currency": g("currency"),
                        
                        "current_price": g("currentPrice"),
                        "long_business_summary": g("longBusinessSummary"),
                        "sector": g("sector"),
                        "industry": g("industry"),
                        "country": g("country"),
                        "state": g("state"),
                        "city": g("city"),
                        "zip": g("zip"),
                        "address_line_1": g("address1"),
                        "address_line_2": g("address2"),
                        "phone": g("phone"),
                        "full_time_employees": g("fullTimeEmployees"),
                        "website": g("website"),
                        "investor_relations_website": g("irWebsite"),
                        "ceo_info": ceo_info,
                        "held_percent_insiders": g("heldPercentInsiders"),
                        "held_percent_institutions": g("heldPercentInstitutions"),
                        "market_state": g("marketState"),
                        "previous_close": g("previousClose"),
                        "volume": g("volume"),
                        # turnover = price * volume
                        "turnover": (g("currentPrice") * g("volume")) if (g("currentPrice") and g("volume")) else None,
                        "open": g("open"),
                        "day_low": g("dayLow"),
                        "day_high": g("dayHigh"),
                        "regular_market_volume": g("regularMarketVolume"),
                        "regular_market_previous_close": g("regularMarketPreviousClose"),
                        "regular_market_open": g("regularMarketOpen"),
                        "regular_market_day_low": g("regularMarketDayLow"),
                        "regular_market_day_high": g("regularMarketDayHigh"),
                        "regular_market_time": g("regularMarketTime"),
                        "regular_market_change_amount": g("regularMarketChange"),
                        "regular_market_change_percent": g("regularMarketChangePercent"),
                        "dividend_rate": g("dividendRate"),
                        "dividend_yield": g("dividendYield"),
                        "ex_dividend_date": g("exDividendDate"),
                        "payout_ratio": g("payoutRatio"),
                        "five_year_avg_dividend_yield": g("fiveYearAvgDividendYield"),
                        "last_dividend_value": g("lastDividendValue"),
                        "last_dividend_date": g("lastDividendDate"),
                        "trailing_annual_dividend_rate": g("trailingAnnualDividendRate"),
                        "trailing_annual_dividend_yield": g("trailingAnnualDividendYield"),
                        "beta": g("beta"),
                        "pe_ttm": g("trailingPE"),
                        # pe_static = currentPrice / trailingEps
                        "pe_static": (g("currentPrice") / g("trailingEps")) if (g("currentPrice") and g("trailingEps")) else None,
                        "pe_dynamic": g("forwardPE"),
                        "price_to_sales_trailing_12_months": g("priceToSalesTrailing12Months"),
                        "price_to_book": g("priceToBook"),
                        "book_value": g("bookValue"),
                        "dividend_ttm": g("trailingAnnualDividendRate"), # Duplicate as per user reg
                        "dividend_yield_ttm": g("trailingAnnualDividendYield"), # Duplicate
                        # turnover_rate = volume / floatShares
                        "turnover_rate": (g("volume") / g("floatShares")) if (g("volume") and g("floatShares")) else None,
                        # turnover_value = currentPrice * floatShares ?? User said "流通值" -> Market Cap of float? 
                        # User formula: currentPrice * floatShares
                        "turnover_value": (g("currentPrice") * g("floatShares")) if (g("currentPrice") and g("floatShares")) else None,
                        # amplitude = (dayHigh - dayLow) / previousClose
                        "amplitude": ((g("dayHigh") - g("dayLow")) / g("previousClose")) if (g("dayHigh") is not None and g("dayLow") is not None and g("previousClose")) else None,
                        # volume_ratio = volume / averageVolume
                        "volume_ratio": (g("volume") / g("averageVolume")) if (g("volume") and g("averageVolume")) else None,
                        # average_price = (high + low) / 2
                        "average_price": ((g("dayHigh") + g("dayLow")) / 2) if (g("dayHigh") is not None and g("dayLow") is not None) else None,
                        "trailing_peg_ratio": g("trailingPegRatio"),
                        "bid": g("bid"),
                        "ask": g("ask"),
                        "bid_size": g("bidSize"),
                        "ask_size": g("askSize"),
                        "average_volume": g("averageVolume"),
                        "average_volume_10days": g("averageVolume10days"),
                        "average_daily_volume_10day": g("averageDailyVolume10Day"),
                        "market_cap": g("marketCap"),
                        "enterprise_value": g("enterpriseValue"),
                        "float_shares": g("floatShares"),
                        "shares_outstanding": g("sharesOutstanding"),
                        "implied_shares_outstanding": g("impliedSharesOutstanding"),
                        "fifty_two_week_low": g("fiftyTwoWeekLow"),
                        "fifty_two_week_high": g("fiftyTwoWeekHigh"),
                        "all_time_high": g("allTimeHigh"), # yf might not have this, but user asked
                        "all_time_low": g("allTimeLow"), # Not directly provided usually
                        "fifty_two_week_range": g("fiftyTwoWeekRange"),
                        "fifty_two_week_change_percent": g("fiftyTwoWeekChangePercent"),
                        "sand_p_52_week_change": g("SandP52WeekChange"),
                        "fifty_day_average": g("fiftyDayAverage"),
                        "two_hundred_day_average": g("twoHundredDayAverage"),
                        "fifty_day_average_change": g("fiftyDayAverageChange"),
                        "fifty_day_average_change_percent": g("fiftyDayAverageChangePercent"),
                        "two_hundred_day_average_change": g("twoHundredDayAverageChange"),
                        "two_hundred_day_average_change_percent": g("twoHundredDayAverageChangePercent"),
                        "shares_short": g("sharesShort"),
                        "shares_short_prior_month": g("sharesShortPriorMonth"),
                        "shares_short_previous_month_date": g("sharesShortPreviousMonthDate"),
                        "date_short_interest": g("dateShortInterest"),
                        "shares_percent_shares_out": g("sharesPercentSharesOut"),
                        "short_ratio": g("shortRatio"),
                        "short_percent_of_float": g("shortPercentOfFloat"),
                        "total_cash": g("totalCash"),
                        "total_cash_per_share": g("totalCashPerShare"),
                        "total_debt": g("totalDebt"),
                        "debt_to_equity": g("debtToEquity"),
                        "total_revenue": g("totalRevenue"),
                        "revenue_per_share": g("revenuePerShare"),
                        "revenue_growth": g("revenueGrowth"),
                        "net_income_to_common": g("netIncomeToCommon"),
                        "earnings_growth": g("earningsGrowth"),
                        "earnings_quarterly_growth": g("earningsQuarterlyGrowth"),
                        "ebitda": g("ebitda"),
                        "enterprise_to_revenue": g("enterpriseToRevenue"),
                        "enterprise_to_ebitda": g("enterpriseToEbitda"),
                        "profit_margin": g("profitMargin"),
                        "gross_margin": g("grossMargin"),
                        "ebitda_margin": g("ebitdaMargin"),
                        "operating_margin": g("operatingMargin"),
                        "return_on_assets": g("returnOnAssets"),
                        "return_on_equity": g("returnOnEquity"),
                        "free_cashflow": g("freeCashflow"),
                        "operating_cashflow": g("operatingCashflow"),
                        "trailing_eps": g("trailingEps"),
                        "forward_eps": g("forwardEps"),
                        "eps_trailing_twelve_months": g("epsTrailingTwelveMonths"), # often same as trailingEps
                        "eps_forward": g("epsForward"), # same as forwardEps
                        "eps_current_year": g("epsCurrentYear"),
                        "price_eps_current_year": g("priceEpsCurrentYear"),
                        "last_split_factor": g("lastSplitFactor"),
                        "last_split_date": g("lastSplitDate"),
                        "pre_market_price": g("preMarketPrice"),
                        "pre_market_change": g("preMarketChange"),
                        "pre_market_change_percent": g("preMarketChangePercent"),
                        "pre_market_time": g("preMarketTime"), # Ensure timestamp is clear? 
                        
                        "post_market_change_percent": g("postMarketChangePercent"),
                        "post_market_price": g("postMarketPrice"),
                        "post_market_change": g("postMarketChange"),
                        "post_market_time": g("postMarketTime"),
                        
                        # Calculated
                        "year_to_date_return": calculated_returns["YTD"],
                        "year_to_date_trading_date_range": calculated_ranges["YTD"],
                        
                        "three_month_return": calculated_returns["3M"],
                        "three_month_trading_date_range": calculated_ranges["3M"],
                        
                        "six_month_return": calculated_returns["6M"],
                        "six_month_trading_date_range": calculated_ranges["6M"],
                        
                        "one_year_return": calculated_returns["1Y"],
                        "one_year_trading_date_range": calculated_ranges["1Y"],
                        
                        "three_year_return": calculated_returns["3Y"],
                        "three_year_trading_date_range": calculated_ranges["3Y"],
                        
                        "five_year_return": calculated_returns["5Y"],
                        "five_year_trading_date_range": calculated_ranges["5Y"],
                        
                        "history": full_history_list if is_return_history else None
                    }
                    
                    # Sanitize (NaN -> None)
                    clean_item = YahooService._sanitize_value(item_data)
                    results.append(clean_item)

                except Exception as inner_e:
                    logger.error(f"Error processing {y_sym}: {inner_e}")
                    # Return partial or empty for this symbol
                    results.append({
                        "symbol": original_info["stock_symbol"],
                        "exchange_acronym": original_info["exchange_acronym"],
                        "yahoo_symbol": y_sym,
                        # Add error note?
                    })
            
            return results

        except Exception as e:
            logger.error(f"Error in get_batch_stock_base_data: {e}")
            return []
