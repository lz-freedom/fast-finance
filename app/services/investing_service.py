import logging
import requests
from typing import Dict, Any, List, Optional
from app.core.config import settings

logger = logging.getLogger("fastapi")

class InvestingService:
    BASE_URL = "https://api.investing.com/api/search/v2/search"

    @classmethod
    def search(cls, keyword: str, country_code: Optional[str] = None, filter_type: bool = True) -> Dict[str, Any]:
        """
        Search for assets on Investing.com
        
        Args:
            keyword: The search term (q)
            country_code: Optional domain-id header (default: None)
            filter_type: Whether to filter results by type (Stock/股票/株式) (default: True)
            
        Returns:
            Dict of search results
        """
        params = {"q": keyword}
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "pragma": "no-cache",
            "Accept": "application/json, text/plain, */*",
        }
        
        if country_code:
            headers["domain-id"] = str(country_code)

        proxies = {}
        if settings.PROXY_INVESTING:
            proxies = {
                "http": settings.PROXY_INVESTING,
                "https": settings.PROXY_INVESTING,
            }

        try:
            logger.info(f"Searching Investing.com for '{keyword}' with headers {headers}")
            response = requests.get(
                cls.BASE_URL, 
                params=params, 
                headers=headers, 
                proxies=proxies, 
                timeout=10
            )
            response.raise_for_status()
            
            data = response.json()
            
            # Remove unused fields
            for field in ["tools", "events", "@pages"]:
                data.pop(field, None)
                
            # Filter quotes by type
            if filter_type and "quotes" in data and isinstance(data["quotes"], list):
                valid_types = ["株式", "股票", "Stock"]
                data["quotes"] = [
                    item for item in data["quotes"]
                    if any(k in item.get("type", "") for k in valid_types)
                ]
                
            return data
            
        except requests.RequestException as e:
            logger.error(f"Error searching Investing.com: {str(e)}")
            # Return empty list or raise custom exception depending on requirements.
            # For now, returning empty list as per service pattern seen in yahoo_service.
            return []

    @classmethod
    def get_translations(cls, symbol: str, country_codes: List[str]) -> Dict[str, List[Dict[str, Any]]]:
        """
        Get translations for a stock symbol, news, and articles across multiple countries.
        """
        # 1. Search in US to get base info and ID (using lowercase 'us' as base)
        us_data = cls.search(symbol, country_code="us")
        
        # Initialize containers
        # Quotes: Map by ID for aggregation
        quotes_map = {}
        # News/Articles: Flat lists
        news_list = []
        articles_list = []
        
        # Helper to process flat items (news/articles)
        def add_flat_items(data: Dict[str, Any], region_code: str):
            for cat, container in [("news", news_list), ("articles", articles_list)]:
                if cat in data and isinstance(data[cat], list):
                    for item in data[cat]:
                        # shallow copy to avoid mutating original if needed, 
                        # though here we just constructed it from json
                        item_copy = item.copy()
                        item_copy["country_code"] = region_code
                        container.append(item_copy)

        # Process US Data
        # 1. Quotes (Base)
        if "quotes" in us_data and isinstance(us_data["quotes"], list):
            for quote in us_data["quotes"]:
                q_id = quote.get("id")
                if q_id:
                    quotes_map[q_id] = {
                        "id": q_id,
                        "symbol": quote.get("symbol"),
                        "exchange": quote.get("exchange"),
                        "description": quote.get("description"),
                        "flag": quote.get("flag"),
                        "type": quote.get("type"),
                        "country_codes": [] # US is implicit base, or could add it here if desired. 
                                          # Requirement says "quotes保持不变", usually implying US is base and others are in list.
                                          # But previous logic had US implicitly as base. 
                                          # Let's keep it as base container.
                    }
        
        # 2. News/Articles (US)
        add_flat_items(us_data, "us")

        # 2. Iterate country codes
        for code in country_codes:
            try:
                # Disable type filtering for translations
                local_data = cls.search(symbol, country_code=code, filter_type=False)
                
                # 1. Quotes (Match against US Base)
                if "quotes" in local_data and isinstance(local_data["quotes"], list):
                     for quote in local_data["quotes"]:
                        q_id = quote.get("id")
                        if q_id in quotes_map:
                            quotes_map[q_id]["country_codes"].append({
                                "country_code": code,
                                "description": quote.get("description")
                            })
                
                # 2. News/Articles (Accumulate)
                add_flat_items(local_data, code)
                                
            except Exception as e:
                logger.warning(f"Failed to fetch translation for {code}: {e}")

        # Return categorized results
        return {
            "quotes": list(quotes_map.values()),
            "news": news_list,
            "articles": articles_list
        }
