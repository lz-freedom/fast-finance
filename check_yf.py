
try:
    import yfinance as yf
    print(f"yfinance version: {yf.__version__}")
    try:
        from yfinance import EquityQuery
        print("EquityQuery found in yfinance")
    except ImportError:
        print("EquityQuery NOT found in yfinance")
    
    if hasattr(yf, 'screen'):
        print("yf.screen found")
    else:
        print("yf.screen NOT found")

except ImportError as e:
    print(f"Error importing yfinance: {e}")
