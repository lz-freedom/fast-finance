import logging
import requests
import json
import time
import threading
from typing import List, Dict, Any, Optional
from datetime import datetime
from app.core.database import SQLiteManager
from app.core.constants import EXCHANGE_MAPPING
from app.schemas.tradingview_sync import SyncTaskStatus, TradingViewStockBase

logger = logging.getLogger("fastapi")

class TradingViewSyncService:
    _instance = None
    _lock = threading.Lock()
    _task_status = SyncTaskStatus(is_running=False, status="Idle", processed_count=0)
    _stop_event = threading.Event()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(TradingViewSyncService, cls).__new__(cls)
        return cls._instance

    @property
    def status(self) -> SyncTaskStatus:
        return self._task_status

    def get_task_status(self) -> SyncTaskStatus:
        return self._task_status

    def start_sync_task(self, ipo_offer_date_type: Optional[str] = None):
        """
        Start the sync task in a background thread if not already running.
        """
        with self._lock:
            if self._task_status.is_running:
                logger.warning("TradingView sync task is already running.")
                return self._task_status

            self._stop_event.clear()
            self._task_status = SyncTaskStatus(
                is_running=True, 
                status="Starting...", 
                processed_count=0,
                last_run_time=datetime.now()
            )
            
        # Run directly in the scheduler's thread/executor
        self._run_sync_process(ipo_offer_date_type)
        
        return self._task_status

    def stop_sync_task(self):
        """
        Signal the running task to stop.
        """
        if self._task_status.is_running:
            self._stop_event.set()
            self._task_status.status = "Stopping..."

    def _run_sync_process(self, ipo_offer_date_type: Optional[str] = None):
        logger.info(f"Starting TradingView sync process (IPO Filter: {ipo_offer_date_type})...")
        try:
            SQLiteManager.init_tradingview_table()
            
            total_processed = 0
            
            # Use defined exchanges or a predefined list of major exchanges if specific traversal is needed.
            # The user request implies "Traverse exchange". We can use EXCHANGE_MAPPING from constants.py
            # But that mapping is limited. The user prompt curl example includes:
            # "right":["SSE","SZSE","HKEX","NYSE","NASDAQ","SGX","TSE","NSE","LSE","TSX"]
            # I will use the acronyms from constant.py plus ensure the curl ones are covered.
            
            # Collect unique acronyms
            exchanges = list(set([item['acronym'] for item in EXCHANGE_MAPPING]))
            
            # Add exchanges from user example if missing
            extra_exchanges = ["SSE", "SZSE", "HKEX", "NYSE", "NASDAQ", "SGX", "TSE", "NSE", "LSE", "TSX"]
            for ex in extra_exchanges:
                if ex not in exchanges:
                    exchanges.append(ex)
            
            logger.info(f"Target exchanges for sync: {exchanges}")
            self._task_status.total_count = 0 # converting to 'unknown' or just tracking processed
            
            for exchange in exchanges:
                if self._stop_event.is_set():
                    break
                    
                self._task_status.status = f"Processing {exchange}..."
                count = self._sync_exchange(exchange, ipo_offer_date_type)
                total_processed += count
                self._task_status.processed_count = total_processed
                
            self._task_status.status = "Completed"
            
        except Exception as e:
            logger.error(f"TradingView sync task failed: {e}")
            self._task_status.status = "Failed"
            self._task_status.last_error = str(e)
        finally:
            self._task_status.is_running = False
            self._task_status.last_run_time = datetime.now()
            
            # Post-sync cleanup
            try:
                cleaned_count = SQLiteManager.cleanup_tradingview_duplicates()
                logger.info(f"Cleanup finished: removed {cleaned_count} duplicates")
            except Exception as e:
                logger.error(f"Cleanup failed: {e}")
                
            logger.info(f"TradingView sync finished. Total processed: {total_processed}")

    def _sync_exchange(self, exchange: str, ipo_offer_date_type: Optional[str] = None) -> int:
        """
        Fetch and save stocks for a specific exchange.
        Handles pagination manually via range.
        """
        processed_count = 0
        BATCH_SIZE = 800 # Match curl example range size
        start = 0
        
        while True:
            if self._stop_event.is_set():
                break
                
            try:
                # Log batch start
                logger.info(f"[{exchange}] Fetching batch range: {start} - {start + BATCH_SIZE}...")
                
                data = self._fetch_from_tradingview(exchange, start, start + BATCH_SIZE, ipo_offer_date_type)
                
                if not data or not data.get('data'):
                    logger.info(f"[{exchange}] No more data received.")
                    break
                    
                items = data['data']
                total_count_resp = data.get('totalCount', 0)
                
                # Transform items for DB
                db_items = []
                for item in items:
                    # item structure: "s": "NASDAQ:NVDA", "d": [{...}, ...]
                    s_value = item.get('s')
                    d_values = item.get('d', [])
                    
                    if not s_value or not d_values:
                        continue
                        
                    meta = d_values[0] if len(d_values) > 0 and isinstance(d_values[0], dict) else {}
                    
                    # Columns indices based on payload:
                    # 0: ticker-view (meta dict)
                    # ...
                    # 18: sector.tr
                    # ...
                    # 20: sector
                    # ...
                    # 23: ipo_offer_date
                    # 24: ipo_offer_price_usd
                    # 25: ipo_deal_amount_usd
                    
                    # Safe extraction helper
                    def get_val(idx):
                        return d_values[idx] if len(d_values) > idx else None
                    
                    def format_date(ts):
                        if ts is None:
                            return None
                        try:
                            # Verify ts type and cast if necessary
                            val = float(ts)
                            # Use datetime.fromtimestamp with utc to handle negative timestamps safely
                            from datetime import timezone
                            dt = datetime.fromtimestamp(val, tz=timezone.utc)
                            return dt.strftime('%Y-%m-%d')
                        except Exception as e:
                            # Log conversion error for debugging if needed, but here just fallback
                            # logger.warning(f"Date formatting failed for {ts}: {e}")
                            return str(ts)

                    # Mapping
                    db_item = {
                        "tradingview_full_stock_symbol": s_value,
                        "stock_symbol": meta.get('name', s_value.split(':')[-1] if ':' in s_value else s_value),
                        "exchange_acronym": meta.get('exchange', exchange),
                        "name": meta.get('name', ''),
                        "description": meta.get('description', ''),
                        "logoid": meta.get('logoid', ''),
                        
                        "sector_tr": get_val(18),
                        "sector": get_val(20),
                        "ipo_offer_date": format_date(get_val(23)),
                        "ipo_offer_price": get_val(24),
                        "ipo_deal_amount": get_val(25)
                    }
                    db_items.append(db_item)
                    
                # Save to DB
                SQLiteManager.upsert_tradingview_batch(db_items)
                processed_count += len(db_items)
                
                # Log batch success
                logger.info(f"[{exchange}] Processed batch items: {len(db_items)}. Total so far: {processed_count}")
                
                # Check if we reached end
                if len(items) < BATCH_SIZE:
                    break
                    
                start += BATCH_SIZE
                
                # Be nice to API
                time.sleep(1.0) # Increased delay slightly to be safer and give better log pacing
                
            except Exception as e:
                logger.error(f"Error syncing exchange {exchange}: {e}")
                # Optional: break or continue? break to avoid infinite loops on error
                break
                
        return processed_count

    def _fetch_from_tradingview(self, exchange: str, range_start: int, range_end: int, ipo_offer_date_type: Optional[str] = None) -> Dict[str, Any]:
        url = 'https://scanner.tradingview.com/global/scan?label-product=popup-screener-stock'
        
        headers = {
            'accept': 'application/json',
            'accept-language': 'zh-CN,zh;q=0.9',
            'content-type': 'text/plain;charset=UTF-8',
            'origin': 'https://cn.tradingview.com',
            'referer': 'https://cn.tradingview.com/',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36'
        }
        
        # Prepare payload
        payload = {
            "columns": [
                "ticker-view", "close", "type", "typespecs", "pricescale", 
                "minmov", "fractional", "minmove2", "currency", "change", 
                "volume", "relative_volume_10d_calc", "market_cap_basic", 
                "fundamental_currency_code", "price_earnings_ttm", 
                "earnings_per_share_diluted_ttm", "earnings_per_share_diluted_yoy_growth_ttm", 
                "dividends_yield_current", "sector.tr", "market", "sector", 
                "AnalystRating", "AnalystRating.tr",
                "ipo_offer_date", "ipo_offer_price_usd", "ipo_deal_amount_usd"
            ],
            "filter": [
                {"left": "exchange", "operation": "equal", "right": exchange},
            ],
            "ignore_unknown_fields": False,
            "options": {"lang": "zh"},
            "price_conversion": {"to_currency": "usd"},
            "range": [range_start, range_end],
            "sort": {"sortBy": "market_cap_basic", "sortOrder": "desc"},
            "symbols": {},
            "markets": ["america", "asia", "europe", "africa", "pacific", "middle_east"] 
        }
        
        # Add IPO Date Filter
        if ipo_offer_date_type:
            date_filter = None
            if ipo_offer_date_type == "day":
                # 当前交易日
                date_filter = {"left": "ipo_offer_date", "operation": "in_day_range", "right": [0, 0]}
            elif ipo_offer_date_type == "yesterday":
                 # 前一天
                date_filter = {"left": "ipo_offer_date", "operation": "in_day_range", "right": [-1, -1]}
            elif ipo_offer_date_type == "week":
                # 本周
                date_filter = {"left": "ipo_offer_date", "operation": "in_week_range", "right": [0, 0]}
            elif ipo_offer_date_type == "month":
                 # 本月
                date_filter = {"left": "ipo_offer_date", "operation": "in_month_range", "right": [0, 0]}
            elif ipo_offer_date_type == "year":
                # 今年
                date_filter = {"left": "ipo_offer_date", "operation": "in_day_range", "right": [-365, -1]} # As per user request: -365 to -1? Or -365 to 0? User example said -365,-1 for "year", wait, year usually means YTD or last 12 months. User said: 
                # // 今年 
                # { "right": [-365, -1] } 
                # I will follow user example strictly.
            
            if date_filter:
                payload["filter"].append(date_filter)

        # Markets list
        payload["markets"] = [
            "america","argentina","australia","austria","bahrain","bangladesh","belgium","brazil",
            "canada","chile","china","colombia","cyprus","czech","denmark","egypt","estonia",
            "finland","france","germany","greece","hongkong","hungary","iceland","india","indonesia",
            "ireland","israel","italy","japan","kenya","kuwait","latvia","lithuania","luxembourg",
            "malaysia","mexico","morocco","netherlands","newzealand","nigeria","norway","pakistan",
            "peru","philippines","poland","portugal","qatar","romania","russia","ksa","serbia",
            "singapore","slovakia","rsa","korea","spain","srilanka","sweden","switzerland","taiwan",
            "thailand","tunisia","turkey","uae","uk","venezuela","vietnam"
        ]
        
        try:
            resp = requests.post(url, headers=headers, data=json.dumps(payload), timeout=30)
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            logger.error(f"Failed to fetch from TradingView (Exchange: {exchange}, Range: {range_start}-{range_end}): {e}")
            return {}

tradingview_sync_service = TradingViewSyncService()
