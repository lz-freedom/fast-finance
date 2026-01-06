import asyncio
import sys
import os
import json
import logging

# Add project root to path
sys.path.append(os.getcwd())

from app.core.database import SQLiteManager
from app.services.yahoo_service import YahooService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def verify():
    print("=== Verifying Yahoo Architecture Refactor ===")
    
    # 1. Initialize DB
    SQLiteManager.init_db()
    print("[OK] DB Initialized")
    
    # 2. Test Web Crawler (Raw Data)
    print("\n--- Testing web_crawler (Raw) ---")
    symbol = "AAPL"
    raw_data = YahooService.web_crawler(symbol)
    
    if not raw_data:
        print("[FAIL] web_crawler returned no data")
        return
        
    print(f"[OK] web_crawler returned data for {symbol}")
    print(f"Returns keys: {list(raw_data.get('returns', {}).keys())}")
    
    compare_len = len(raw_data.get('analysis_compare_to', []))
    watch_len = len(raw_data.get('analysis_people_also_watch', []))
    print(f"Compare To: {compare_len} items")
    print(f"People Also Watch: {watch_len} items")
    
    # 3. Test Enrichment Logic
    print("\n--- Testing get_related_stock (Enrichment) ---")
    
    # 3.1 First call (Empty DB) -> Should return empty lists (Discard all)
    print("Testing with Empty yahoo_stock table...")
    related = YahooService.get_related_stock("AAPL", "NASDAQ")
    print(f"Result (Empty DB) Compare To: {len(related['compare_to_list'])}")
    
    # Verify Discard Logic: If DB is empty, should be 0 (unless one of them IS AAPL? no, related stocks)
    # Actually, get_related_stock queries DB for the RELATED symbols.
    # Since DB is empty, it finds nothing, so it should return empty lists.
    
    # 3.2 Insert Mock Data
    print("Inserting Mock Data into yahoo_stock...")
    
    # Pick some symbols from raw data to mock
    mock_items = []
    
    limit = 3
    count = 0
    for item in raw_data.get('analysis_compare_to', []):
        s = item.get('stock_symbol')
        if s:
            mock_items.append({
                "yahoo_stock_symbol": s,
                "yahoo_exchange_symbol": "NMS", # Mock
                "stock_symbol": s,
                "exchange_acronym": "NASDAQ",
                "name": f"Mock {s}"
            })
            count += 1
            if count >= limit: break
            
    SQLiteManager.upsert_yahoo_stock_batch(mock_items)
    print(f"[OK] Inserted {len(mock_items)} mock items")
    
    # 3.3 Second call (Populated DB) -> Should return enriched items
    related_enriched = YahooService.get_related_stock("AAPL", "NASDAQ")
    res_compare = related_enriched['compare_to_list']
    
    print(f"Result (Mock DB) Compare To: {len(res_compare)}")
    
    if len(res_compare) == len(mock_items):
         print("[OK] Enrichment working correctly. Found expected number of items.")
    else:
         print(f"[FAIL] Expected {len(mock_items)} items, got {len(res_compare)}")
         print(f"Mocked: {[i['yahoo_stock_symbol'] for i in mock_items]}")
         print(f"Result: {[i['stock_symbol'] for i in res_compare]}")

    # 4. Check Cache
    print("\n--- Checking Cache ---")
    cache = SQLiteManager.get_yahoo_stock_related_cache("AAPL") # AAPL is the yahoo symbol
    if cache:
        print("[OK] Cache entry exists for AAPL")
    else:
        print("[FAIL] Cache entry missing for AAPL")

    print("\n=== Verification Complete ===")

if __name__ == "__main__":
    asyncio.run(verify())
