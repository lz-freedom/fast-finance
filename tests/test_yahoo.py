from fastapi.testclient import TestClient
from app.main import app
import json

client = TestClient(app)

def test_yahoo_info():
    print("\n[TEST] Info...")
    response = client.post("/api/v1/yahoo/info", json={"symbol": "AAPL"})
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    print("Info API: OK")

def test_yahoo_history():
    print("\n[TEST] History...")
    payload = {
        "symbol": "AAPL",
        "period": "5d",
        "interval": "1d"
    }
    response = client.post("/api/v1/yahoo/history", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert isinstance(data["data"], list)
    print("History API: OK")

def test_yahoo_news():
    print("\n[TEST] News...")
    response = client.post("/api/v1/yahoo/news", json={"symbol": "AAPL"})
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    print(f"News items: {len(data.get('data', []))}")
    print("News API: OK")

def test_yahoo_holders():
    print("\n[TEST] Holders...")
    response = client.post("/api/v1/yahoo/holders", json={"symbol": "AAPL"})
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    holders = data["data"]
    # Check keys exist even if data is empty/null
    assert "major_holders" in holders
    assert "institutional_holders" in holders
    print("Holders API: OK")

def test_yahoo_analysis():
    print("\n[TEST] Analysis...")
    response = client.post("/api/v1/yahoo/analysis", json={"symbol": "AAPL"})
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    print("Analysis API: OK")

def test_yahoo_calendar():
    print("\n[TEST] Calendar...")
    response = client.post("/api/v1/yahoo/calendar", json={"symbol": "AAPL"})
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    print("Calendar API: OK")

if __name__ == "__main__":
    try:
        test_yahoo_info()
        test_yahoo_history()
        test_yahoo_news()
        test_yahoo_holders()
        test_yahoo_analysis()
        test_yahoo_calendar()
        print("\nAll Yahoo Finance Extended tests passed!")
    except Exception as e:
        print(f"\nTest Failed: {e}")
