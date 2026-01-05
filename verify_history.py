import sys
import os

# Mocking modules to separate test logic from dependencies
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("test")

# Replicate the core logic function or import it if possible
# Since we can't easily import the full FastAPI app context without envs, 
# typically we'd use a mock or unit test. 
# Here I will write a simple test that MOCKS the YahooService call behavior 
# to ensure my logic understanding is correct, OR I can try to import the service 
# directly if I mock the dependencies.

# Better: Let's create a small script that imports the Service and runs it 
# just like verify_resolution.py did (since that worked).
# We just need to make sure we pass the correct arguments.

sys.path.append(os.getcwd())
try:
    from app.services.yahoo_service import YahooService, yf
    # We might need to mock yf if we don't want real network calls, 
    # but for verification real calls are better.
except ImportError:
    print("Could not import YahooService. Ensure env is correct.")
    sys.exit(1)

def test_history_toggle():
    items = [{"stock_symbol": "AAPL", "exchange_acronym": "NASDAQ"}]
    
    print("--- Test 1: is_return_history = True ---")
    results_true = YahooService.get_batch_stock_base_data(items, is_return_history=True)
    if results_true:
        hist = results_true[0].get("history")
        if hist and len(hist) > 0:
            print(f"PASS: History returned. Check len: {len(hist)}")
        else:
            print("FAIL: History expected but empty/None")
    else:
        print("FAIL: No results")

    print("\n--- Test 2: is_return_history = False ---")
    results_false = YahooService.get_batch_stock_base_data(items, is_return_history=False)
    if results_false:
        hist = results_false[0].get("history")
        if hist is None:
            print("PASS: History is None as expected")
        else:
            print(f"FAIL: History should be None, got {type(hist)}")
            
        # Check if calculations still worked (e.g. 5Y return)
        ret_5y = results_false[0].get("five_year_return")
        if ret_5y is not None:
             print(f"PASS: 5Y Return calculated: {ret_5y}")
        else:
             print("WARNING: 5Y Return is None (could be valid if data missing, but likely should exist for AAPL)")

if __name__ == "__main__":
    test_history_toggle()
