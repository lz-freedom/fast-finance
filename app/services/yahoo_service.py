import yfinance as yf
from yfinance import EquityQuery
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

    @staticmethod
    def get_scraped_analysis(symbol: str) -> Dict[str, Any]:
        """
        Scrapes additional analysis data from Yahoo Finance web page:
        - Performance Overview (Returns vs Index)
        - Compare To (Competitors with Name)
        - People Also Watch (Related Stocks with Name)
        """
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
            import re
            soup = BeautifulSoup(resp.text, "html.parser")
            
            result = {
                "returns": {},
                "compare_to": [],
                "people_also_watch": []
            }
            
            # 1. Performance Overview (Stock vs Index)
            # Structure: section[data-testid="performance-overview"] -> section[data-testid="card-container"]
            perf_section = soup.find("section", {"data-testid": "performance-overview"})
            if perf_section:
                cards = perf_section.find_all("section", {"data-testid": "card-container"})
                for card in cards:
                    # Get Title
                    title_div = card.find("h3", class_="title")
                    if not title_div:
                        continue
                    title_text = title_div.get_text(strip=True) # e.g. "YTD Return"
                    
                    # Normalize key
                    key = None
                    if "YTD" in title_text: key = "YTD"
                    elif "1-Year" in title_text: key = "1-Year"
                    elif "3-Year" in title_text: key = "3-Year"
                    elif "5-Year" in title_text: key = "5-Year"
                    
                    if key:
                        # Get rows
                        # Structure: div class="cards-4 perfInfo ..." -> div (row) -> div.symbol, div.perf
                        # Note: The class name might contain hashes, rely on structure or partial class
                        info_div = card.find("div", class_=lambda x: x and "perfInfo" in x)
                        if info_div:
                            # Direct children divs are the rows
                            rows = info_div.find_all("div", recursive=False)
                            if len(rows) >= 2:
                                # Row 1: Stock
                                stock_perf = rows[0].find("div", class_=lambda x: x and "perf" in x)
                                
                                # Row 2: Index
                                index_row = rows[1]
                                index_perf = index_row.find("div", class_=lambda x: x and "perf" in x)
                                index_symbol = index_row.find("div", class_=lambda x: x and "symbol" in x)
                                
                                result["returns"][key] = {
                                    "stock": stock_perf.get_text(strip=True) if stock_perf else "",
                                    "index": index_perf.get_text(strip=True) if index_perf else "",
                                    "index_name": index_symbol.get_text(strip=True) if index_symbol else ""
                                }
                            elif len(rows) == 1:
                                stock_perf = rows[0].find("div", class_=lambda x: x and "perf" in x)
                                result["returns"][key] = {
                                    "stock": stock_perf.get_text(strip=True) if stock_perf else "",
                                    "index": None,
                                    "index_name": None
                                }

            # Helper to extract tickers from cards
            def extract_from_cards(section_testid, key):
                section = soup.find("section", {"data-testid": section_testid})
                if section:
                    # Find cards
                    cards = section.find_all("section", {"data-testid": "card-container"})
                    for card in cards:
                        # Strategy 1: Compare To structure
                        # <div class="tickerContainer"> <a ...> <div> <span>SYMBOL</span> <div class="longName">NAME</div> </div> </a>
                        ticker_container = card.find("div", class_=lambda x: x and "tickerContainer" in x)
                        if ticker_container:
                            a_tag = ticker_container.find("a")
                            if a_tag:
                                # Symbol
                                span = a_tag.find("span")
                                # Name
                                long_name = a_tag.find("div", class_=lambda c: c and "longName" in c)
                                if span and long_name:
                                    s = span.get_text(strip=True)
                                    n = long_name.get_text(strip=True)
                                    if s and s != symbol:
                                        result[key].append({"symbol": s, "name": n})
                                        continue

                        # Strategy 2: People Also Watch structure
                        # <div class="ticker-container"> ... <div data-testid="ticker-container"> ... <span class="symbol">SYMBOL</span> <span class="longName">NAME</span>
                        # Note: People also watch has .ticker-container (lowercase/hyphen) vs tickerContainer
                        # Let's try to find symbol and longName directly in the card if generic
                        
                        sym_span = card.find("span", class_=lambda x: x and "symbol" in x)
                        name_span = card.find(class_=lambda x: x and "longName" in x)
                        
                        if sym_span:
                            s = sym_span.get_text(strip=True)
                            n = name_span.get_text(strip=True) if name_span else ""
                            # Sometimes name is in title attribute
                            if not n and name_span and name_span.has_attr("title"):
                                n = name_span["title"]
                            
                            if s and s != symbol:
                                result[key].append({"symbol": s, "name": n})

            # 2. Compare To
            extract_from_cards("compare-to", "compare_to")
            
            # 3. People Also Watch
            extract_from_cards("people-also-watch", "people_also_watch")

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
