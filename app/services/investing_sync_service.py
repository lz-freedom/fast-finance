import requests
import time
import random
import logging
import threading
from typing import List, Dict, Any, Optional

from app.core.database import DBManager
from app.core.constants import get_all_exchanges, PLATFORM_INVESTING
from app.schemas.response import BaseResponse
from app.schemas.tradingview_sync import SyncTaskStatus

logger = logging.getLogger(__name__)

class InvestingSyncService:
    def __init__(self):
        self._is_running = False
        self._task_status = SyncTaskStatus(
            is_running=False,
            status="Idle",
            processed_count=0,
            total_count=0
        )
        self._lock = threading.Lock()
        
    def get_task_status(self) -> SyncTaskStatus:
        return self._task_status

    def start_sync_task(self) -> SyncTaskStatus:
        with self._lock:
            if self._is_running:
                return self._task_status
            
            self._is_running = True
            self._task_status = SyncTaskStatus(
                is_running=True,
                status="Starting...",
                processed_count=0,
                total_count=0,
                last_run_time=time.strftime("%Y-%m-%dT%H:%M:%S")
            )
            
            # Run directly in the scheduler's thread/executor
            self._run_sync_process()
            
            return self._task_status

    def _run_sync_process(self):
        logger.info("Starting Investing.com sync process...")
        total_processed = 0
        try:
            exchanges = get_all_exchanges()
            
            for exchange_info in exchanges:
                # 检查是否有 Investing 配置
                if not exchange_info.get("investing_code"):
                    continue
                
                acronym = exchange_info["acronym"]
                
                # Check for stop signal
                if not self._is_running:
                    break

                self._task_status.status = f"Processing {acronym}..."
                
                try:
                    count = self._sync_exchange(exchange_info)
                    total_processed += count
                    self._task_status.processed_count = total_processed
                except Exception as e:
                    logger.error(f"Error syncing {acronym}: {e}")
                    self._task_status.last_error = f"{acronym}: {str(e)}"

            self._task_status.status = "Completed"
        except Exception as e:
            logger.error(f"Sync process failed: {e}")
            self._task_status.last_error = str(e)
            self._task_status.status = "Failed"
        finally:
            self._is_running = False
            self._task_status.is_running = False
            logger.info(f"Investing sync finished. Total processed: {total_processed}")

    def _sync_exchange(self, exchange_info: Dict[str, str]) -> int:
        acronym = exchange_info["acronym"]
        market_code = exchange_info.get("country_code", "cn").upper() # default cn implies market CN? 
        # Wait, country_code in constants: 'cn' -> market 'CN'. 'us' -> market? 'US'?
        # User example: market: "CN".
        # Let's map country_code to market code roughly.
        market_map = {"cn": "CN", "hk": "HK", "us": "US", "uk": "GB", "sg": "SG", "jp": "JP", "in": "IN", "ca": "CA", "au": "AU", "kr": "KR", "tw": "TW"}
        market = market_map.get(exchange_info.get("country_code", "").lower(), "CN")
        
        exchange_name = exchange_info["investing_code"] # e.g. "Shanghai"
        
        logger.info(f"[{acronym}] Fetching CN data (market={market}, exchange={exchange_name})...")
        # 1. Fetch CN Data
        cn_rows_map = self._fetch_all_rows(domain_id="cn", market=market, exchange=exchange_name)
        logger.info(f"[{acronym}] Fetched {len(cn_rows_map)} CN rows.")
        
        logger.info(f"[{acronym}] Fetching EN data (market={market}, exchange={exchange_name})...")
        # 2. Fetch EN Data
        en_rows_map = self._fetch_all_rows(domain_id="us", market=market, exchange=exchange_name)
        logger.info(f"[{acronym}] Fetched {len(en_rows_map)} EN rows.")
        
        # 3. Merge and Save
        merged_items = []
        
        # Iterate over CN rows (primary source)
        for pair_id, cn_row in cn_rows_map.items():
            en_row = en_rows_map.get(pair_id)
            
            # Extract fields
            # Row structure: {"asset": {...}, "data": [...]}
            asset_cn = cn_row.get("asset", {})
            data_cn = cn_row.get("data", [])
            
            asset_en = en_row.get("asset", {}) if en_row else {}
            data_en = en_row.get("data", []) if en_row else []
            
            # Safe getters
            def get_data_val(data_list, idx):
                return data_list[idx].get("value") if len(data_list) > idx else None
            
            # Construct DB Item
            # tradingview_full_stock_symbol construction: ACRONYM:TICKER
            # Ticker is in asset['ticker']
            ticker = asset_cn.get("ticker", "")
            
            # DEBUG: Log Ford
            if ticker == 'F':
                logger.info(f"Processing Ford (F): CN_PairID={pair_id}, EN_Found={en_row is not None}, CN_Name={asset_cn.get('name')}, EN_Name={asset_en.get('name')}")
            
            tv_symbol = f"{acronym}:{ticker}" if ticker else ""
            
            item = {
                "investing_stock_pair_id": pair_id,
                "investing_stock_uid": asset_cn.get("uid"),
                "tradingview_full_stock_symbol": tv_symbol,
                "stock_symbol": ticker,
                "exchange_acronym": acronym,
                "logo_url": asset_cn.get("logo"),
                
                "name_cn": asset_cn.get("name"),
                "name_en": asset_en.get("name"), # Might match ticker or English name
                
                # data[1] is Sector, data[2] is Industry (based on user Example columns order)
                # Metrics: ["investing_exchange", "investing_sector", "investing_industry"]
                "investing_sector_cn": get_data_val(data_cn, 1),
                "investing_sector_en": get_data_val(data_en, 1),
                
                "investing_industry_cn": get_data_val(data_cn, 2),
                "investing_industry_en": get_data_val(data_en, 2),
            }
            merged_items.append(item)
        
        # Batch Upsert
        # Process in chunks of 500
        processed = 0
        chunk_size = 500
        for i in range(0, len(merged_items), chunk_size):
            chunk = merged_items[i:i + chunk_size]
            DBManager.upsert_investing_batch(chunk)
            processed += len(chunk)
            
        return processed

    def _fetch_all_rows(self, domain_id: str, market: str, exchange: str) -> Dict[int, Dict]:
        """
        Fetch all pages for a given domain/market/exchange.
        Returns a map of pairID -> row object.
        """
        all_rows = {}
        skip = 0
        limit = 100
        
        while True:
            try:
                # Random requested-with (numeric) as per user feedback
                rand_suffix = "".join([random.choice("0123456789") for _ in range(8)])
                
                headers = {
                    "domain-id": domain_id,
                    "x-requested-with": f"investing-client/{rand_suffix}",
                    "Content-Type": "application/json",
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
                }
                
                payload = {
                    "query": {
                        "filters": [],
                        "sort": {
                            "metric": "marketcap_adj_latest",
                            "direction": "DESC"
                        },
                        "prefilters": {
                            "primaryOnly": True,
                            "market": market,
                            "exchange": [exchange]
                        }
                    },
                    "metrics": [
                        "investing_exchange",
                        "investing_sector",
                        "investing_industry"
                    ],
                    "page": {
                        "skip": skip,
                        "limit": limit
                    }
                }
                
                url = "https://www.investing.com/pro/_/screener-v2/query"
                
                proxies = None
                from app.core.config import settings
                if settings.PROXY_INVESTING:
                    proxies = {
                        "http": settings.PROXY_INVESTING,
                        "https": settings.PROXY_INVESTING
                    }
                
                # Log request start (debug level to avoid spam, or info if needed for debugging now)
                logger.info(f"Requesting page: domain={domain_id}, market={market}, exchange={exchange}, skip={skip}, limit={limit}")
                
                resp = requests.post(url, json=payload, headers=headers, timeout=30, proxies=proxies)
                
                if resp.status_code != 200:
                    logger.error(f"Investing API error: {resp.status_code} - {resp.text[:500]} - Params: skip={skip}, market={market}, exchange={exchange}")
                    break
                    
                data = resp.json()
                rows = data.get("rows", [])
                
                logger.info(f"Page fetched: {len(rows)} rows. (Total collected so far: {len(all_rows) + len(rows)})")
                
                if not rows:
                    logger.info("Empty rows returned, stopping pagination.")
                    break
                    
                for row in rows:
                    pair_id = row.get("asset", {}).get("pairID")
                    if pair_id:
                        all_rows[pair_id] = row
                
                # Check pagination
                current_rows_count = len(rows)
                if current_rows_count < limit:
                    logger.info(f"Fetched fewer rows than limit ({current_rows_count} < {limit}), stopping pagination.")
                    break
                    
                skip += limit
                
                # Rate limit protection
                time.sleep(2)
            except Exception as e:
                logger.error(f"Error fetching data at skip={skip}: {e}")
                break
                
        return all_rows

investing_sync_service = InvestingSyncService()
