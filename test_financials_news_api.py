import requests
import json
import time

def test_financials():
    url = "http://localhost:9130/api/v1/yahoo/financials"
    payload = {
        "stock_symbol": "AAPL",
        "exchange_acronym": "NASDAQ",
        "type": "income",
        "freq": "yearly"
    }
    headers = {'Content-Type': 'application/json'}
    
    print(f"\n[Financials] Sending POST to {url}")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get("code") == "success" or data.get("code") == "200000": # Accept both success codes
                fin_data = data.get('data')
                print("Test Passed: Financials Success")
                
                if isinstance(fin_data, list) and len(fin_data) > 0:
                    first_item = fin_data[0]
                    print("Sample Item Keys:")
                    print(", ".join(list(first_item.keys())[:10]))
                    
                    # Verify camelCase
                    if "totalRevenue" in first_item:
                        print("CamelCase Check: totalRevenue found!")
                    elif "TotalRevenue" in first_item:
                        print("CamelCase Check FAILED: TotalRevenue found (PascalCase)")
                    else:
                        print("CamelCase Check: totalRevenue missing but keys available")
            else:
                print("Test Failed: API returned success=False")
                print(data)
        else:
            print("Test Failed: HTTP Status not 200")
            print(response.text)
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    test_financials()
