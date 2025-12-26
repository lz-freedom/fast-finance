import yfinance as yf
import requests
import json

symbol = "002594.SZ"

print("--- Checking yfinance info ---")
try:
    ticker = yf.Ticker(symbol)
    info = ticker.info
    # Check for relevant keys
    possible_keys = [k for k in info.keys() if "return" in k.lower() or "recommend" in k.lower()]
    print(f"Relevant keys in info: {possible_keys}")
    # Print a sample to see values
    print(json.dumps({k: info[k] for k in possible_keys}, indent=2))
except Exception as e:
    print(f"yfinance failed: {e}")

print("\n--- Checking requests with headers ---")
url = f"https://finance.yahoo.com/quote/{symbol}"
headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9"
}
try:
    resp = requests.get(url, headers=headers)
    print(f"Status Code: {resp.status_code}")
    if resp.status_code == 200:
        print("Successfully fetched HTML")
        # Save a snippet to check content
        with open("yahoo_page_snippet.html", "w") as f:
            f.write(resp.text[:50000]) # First 50k chars might contain something
    else:
        print("Failed to fetch HTML")
except Exception as e:
    print(f"requests failed: {e}")
