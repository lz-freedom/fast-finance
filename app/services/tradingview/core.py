
import requests
import json
import datetime
import logging
import warnings
from typing import List, Dict, Optional, Any, Union
from .technicals import Compute, Recommendation
from app.schemas.tradingview import ScreenerEnum, IntervalEnum
from app.core.config import settings

logger = logging.getLogger(__name__)

class Analysis:
    def __init__(self):
        self.exchange = ""
        self.symbol = ""
        self.screener = ""
        self.time = None
        self.interval = ""
        self.summary = {}
        self.oscillators = {}
        self.moving_averages = {}
        self.indicators = {}

class TradingView:
    # 核心指标列表，来自于 tradingview-ta 库
    # 不要修改顺序，因为 TradingView API 返回的是没有 Key 的数组，顺序必须严格匹配
    indicators = [
        "Recommend.Other", "Recommend.All", "Recommend.MA", "RSI", "RSI[1]", "Stoch.K", "Stoch.D", "Stoch.K[1]", "Stoch.D[1]", 
        "CCI20", "CCI20[1]", "ADX", "ADX+DI", "ADX-DI", "ADX+DI[1]", "ADX-DI[1]", "AO", "AO[1]", "Mom", "Mom[1]", 
        "MACD.macd", "MACD.signal", "Rec.Stoch.RSI", "Stoch.RSI.K", "Rec.WR", "W.R", "Rec.BBPower", "BBPower", 
        "Rec.UO", "UO", "close", "EMA5", "SMA5", "EMA10", "SMA10", "EMA20", "SMA20", "EMA30", "SMA30", "EMA50", 
        "SMA50", "EMA100", "SMA100", "EMA200", "SMA200", "Rec.Ichimoku", "Ichimoku.BLine", "Rec.VWMA", "VWMA", 
        "Rec.HullMA9", "HullMA9", "Pivot.M.Classic.S3", "Pivot.M.Classic.S2", "Pivot.M.Classic.S1", "Pivot.M.Classic.Middle", 
        "Pivot.M.Classic.R1", "Pivot.M.Classic.R2", "Pivot.M.Classic.R3", "Pivot.M.Fibonacci.S3", "Pivot.M.Fibonacci.S2", 
        "Pivot.M.Fibonacci.S1", "Pivot.M.Fibonacci.Middle", "Pivot.M.Fibonacci.R1", "Pivot.M.Fibonacci.R2", "Pivot.M.Fibonacci.R3", 
        "Pivot.M.Camarilla.S3", "Pivot.M.Camarilla.S2", "Pivot.M.Camarilla.S1", "Pivot.M.Camarilla.Middle", "Pivot.M.Camarilla.R1", 
        "Pivot.M.Camarilla.R2", "Pivot.M.Camarilla.R3", "Pivot.M.Woodie.S3", "Pivot.M.Woodie.S2", "Pivot.M.Woodie.S1", 
        "Pivot.M.Woodie.Middle", "Pivot.M.Woodie.R1", "Pivot.M.Woodie.R2", "Pivot.M.Woodie.R3", "Pivot.M.Demark.S1", 
        "Pivot.M.Demark.Middle", "Pivot.M.Demark.R1", "open", "P.SAR", "BB.lower", "BB.upper", "AO[2]", "volume", "change", "low", "high"
    ]

    scan_url = "https://scanner.tradingview.com/"
    
    # 标准浏览器 Headers，防止 WAF 拦截
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
        "Accept": "*/*",
        "Accept-Language": "en-US,en;q=0.9",
        "Origin": "https://www.tradingview.com",
        "Referer": "https://www.tradingview.com/",
        "Sec-Ch-Ua": '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
        "Sec-Ch-Ua-Mobile": "?0",
        "Sec-Ch-Ua-Platform": '"macOS"',
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-site",
    }

    @staticmethod
    def request(method: str, url: str, **kwargs) -> requests.Response:
        """Unified request handler with proxy support"""
        kwargs.setdefault("headers", TradingView.headers)
        kwargs.setdefault("timeout", 10)
        
        if settings.PROXY_TRADINGVIEW:
            kwargs["proxies"] = {
                "http": settings.PROXY_TRADINGVIEW,
                "https": settings.PROXY_TRADINGVIEW
            }
            
        return requests.request(method, url, **kwargs)

    @staticmethod
    def data(symbols: List[str], interval: str, indicators: List[str]) -> dict:
        """Format TradingView's Scanner Post Data"""
        interval_map = {
            "1m": "|1", "5m": "|5", "15m": "|15", "30m": "|30",
            "1h": "|60", "2h": "|120", "4h": "|240",
            "1W": "|1W", "1M": "|1M"
        }
        
        # 默认 1d (空字符串)
        data_interval = interval_map.get(interval, "")
        if interval == "1d": 
            data_interval = ""
            
        json_body = {
            "symbols": {
                "tickers": [symbol.upper() for symbol in symbols],
                "query": {"types": []}
            },
            "columns": [x + data_interval for x in indicators]
        }
        return json_body

    @staticmethod
    def search(text: str, type_filter: str = None) -> List[dict]:
        """Search for assets on TradingView using custom headers to bypass WAF"""
        url = "https://symbol-search.tradingview.com/symbol_search"
        params = {"text": text, "type": type_filter}
        
        # 强制 GET 请求，这是绕过 WAF 的关键
        try:
            res = TradingView.request("GET", url, params=params)
            res.raise_for_status() # 抛出非 200 异常
            
            # 安全解析 JSON
            symbols = res.json()
            
            results = []
            for symbol in symbols:
                logo = None
                if "logoid" in symbol:
                    logo = f"https://s3-symbol-logo.tradingview.com/{symbol['logoid']}.svg"
                elif "base-currency-logoid" in symbol:
                    logo = f"https://s3-symbol-logo.tradingview.com/{symbol['base-currency-logoid']}.svg"
                elif "country" in symbol:
                    logo = f"https://s3-symbol-logo.tradingview.com/country/{symbol['country']}.svg"
                    
                results.append({
                    "symbol": symbol["symbol"],
                    "exchange": symbol["exchange"],
                    "type": symbol.get("type", ""),
                    "description": symbol.get("description", ""),
                    "logo": logo
                })
            return results
            
        except Exception as e:
            logger.error(f"TradingView Search Error: {e}")
            raise e


def calculate(indicators_val: dict, indicators_key: List[str], screener: str, symbol: str, exchange: str, interval: str) -> Analysis:
    """内部计算函数，处理指标数据并生成推荐信结果"""
    # 初始化计数器
    oscillators_counter = {"BUY": 0, "SELL": 0, "NEUTRAL": 0}
    ma_counter = {"BUY": 0, "SELL": 0, "NEUTRAL": 0}
    computed_oscillators = {}
    computed_ma = {}

    # 将 dict values 转为 list 方便索引访问
    # 注意: indicators_key 的顺序和 indicators_val 的构建顺序需要一致
    # 但这里传入的是 dict名为 indicators_val，实际上我们需要按 key 顺序取出 values
    # 为了兼容原版逻辑，这里假设 indicators_val 已经包含了所有 key
    # 我们可以直接用 list(indicators_val.values()) 吗？ 不行，因为 python < 3.7 dict 无序 (虽然现在都 3.10了)
    # 最稳妥是按 indicators_key 顺序取值
    
    ind_values = [indicators_val.get(k) for k in indicators_key]
    
    # 辅助函数：安全获取指标值
    def get_ind(index):
        if index < len(ind_values):
            return ind_values[index]
        return None
        
    # --- RECOMMENDATIONS ---
    # 0: Recommend.Other, 1: Recommend.All, 2: Recommend.MA
    recommend_oscillators = Compute.Recommend(get_ind(0))
    recommend_summary = Compute.Recommend(get_ind(1))
    recommend_moving_averages = Compute.Recommend(get_ind(2))

    # 如果核心推荐数据缺失，无法继续
    if None in [get_ind(0), get_ind(1)]:
        return None

    # --- OSCILLATORS ---
    # RSI (14): 3: RSI, 4: RSI[1]
    if None not in [get_ind(3), get_ind(4)]:
        res = Compute.RSI(get_ind(3), get_ind(4))
        computed_oscillators["RSI"] = res
        oscillators_counter[res] += 1
        
    # Stoch %K: 5: Stoch.K, 6: Stoch.D, 7: Stoch.K[1], 8: Stoch.D[1]
    if None not in [get_ind(5), get_ind(6), get_ind(7), get_ind(8)]:
        res = Compute.Stoch(get_ind(5), get_ind(6), get_ind(7), get_ind(8))
        computed_oscillators["STOCH.K"] = res
        oscillators_counter[res] += 1
        
    # CCI (20): 9: CCI20, 10: CCI20[1]
    if None not in [get_ind(9), get_ind(10)]:
        res = Compute.CCI20(get_ind(9), get_ind(10))
        computed_oscillators["CCI"] = res
        oscillators_counter[res] += 1
        
    # ADX (14): 11: ADX, 12: ADX+DI, 13: ADX-DI, 14: ADX+DI[1], 15: ADX-DI[1]
    if None not in [get_ind(11), get_ind(12), get_ind(13), get_ind(14), get_ind(15)]:
        res = Compute.ADX(get_ind(11), get_ind(12), get_ind(13), get_ind(14), get_ind(15))
        computed_oscillators["ADX"] = res
        oscillators_counter[res] += 1
        
    # AO: 16: AO, 17: AO[1], 86: AO[2] (注意 86 是后来加在最后的)
    # TradingView.indicators 列表长度检查: len is about 91
    # 86 index 对应 "AO[2]"
    if None not in [get_ind(16), get_ind(17), get_ind(86)]:
        res = Compute.AO(get_ind(16), get_ind(17), get_ind(86))
        computed_oscillators["AO"] = res
        oscillators_counter[res] += 1
        
    # Mom (10): 18: Mom, 19: Mom[1]
    if None not in [get_ind(18), get_ind(19)]:
        res = Compute.Mom(get_ind(18), get_ind(19))
        computed_oscillators["Mom"] = res
        oscillators_counter[res] += 1
        
    # MACD: 20: MACD.macd, 21: MACD.signal
    if None not in [get_ind(20), get_ind(21)]:
        res = Compute.MACD(get_ind(20), get_ind(21))
        computed_oscillators["MACD"] = res
        oscillators_counter[res] += 1
        
    # Stoch RSI: 22: Rec.Stoch.RSI
    if get_ind(22) is not None:
        res = Compute.Simple(get_ind(22))
        computed_oscillators["Stoch.RSI"] = res
        oscillators_counter[res] += 1
        
    # W%R: 24: Rec.WR
    if get_ind(24) is not None:
        res = Compute.Simple(get_ind(24))
        computed_oscillators["W%R"] = res
        oscillators_counter[res] += 1
        
    # BBPower: 26: Rec.BBPower
    if get_ind(26) is not None:
        res = Compute.Simple(get_ind(26))
        computed_oscillators["BBP"] = res
        oscillators_counter[res] += 1
        
    # UO: 28: Rec.UO
    if get_ind(28) is not None:
        res = Compute.Simple(get_ind(28))
        computed_oscillators["UO"] = res
        oscillators_counter[res] += 1

    # --- MOVING AVERAGES ---
    ma_list = ["EMA10", "SMA10", "EMA20", "SMA20", "EMA30", "SMA30",
               "EMA50", "SMA50", "EMA100", "SMA100", "EMA200", "SMA200"]
    # 30: close
    close = get_ind(30)
    # MA indicators start at index 33 to 44 (12 items)
    # 33: EMA10 ... 44: SMA200
    ma_indices = range(33, 45)
    
    if close is not None:
        for i, idx in enumerate(ma_indices):
            val = get_ind(idx)
            if val is not None:
                res = Compute.MA(val, close)
                computed_ma[ma_list[i]] = res
                ma_counter[res] += 1
                
    # Ichimoku: 45: Rec.Ichimoku
    if get_ind(45) is not None:
        res = Compute.Simple(get_ind(45))
        computed_ma["Ichimoku"] = res
        ma_counter[res] += 1
        
    # VWMA: 47: Rec.VWMA
    if get_ind(47) is not None:
        res = Compute.Simple(get_ind(47))
        computed_ma["VWMA"] = res
        ma_counter[res] += 1
        
    # HullMA: 49: Rec.HullMA9
    if get_ind(49) is not None:
        res = Compute.Simple(get_ind(49))
        computed_ma["HullMA"] = res
        ma_counter[res] += 1

    # 构建最终对象
    analysis = Analysis()
    analysis.screener = screener
    analysis.exchange = exchange
    analysis.symbol = symbol
    analysis.interval = interval
    analysis.time = datetime.datetime.now()
    
    # 将指标数据完整附带
    for i, key in enumerate(indicators_key):
        if i < len(ind_values):
            analysis.indicators[key] = ind_values[i]
            
    analysis.oscillators = {
        "RECOMMENDATION": recommend_oscillators,
        "BUY": oscillators_counter["BUY"],
        "SELL": oscillators_counter["SELL"],
        "NEUTRAL": oscillators_counter["NEUTRAL"],
        "COMPUTE": computed_oscillators
    }
    analysis.moving_averages = {
        "RECOMMENDATION": recommend_moving_averages,
        "BUY": ma_counter["BUY"],
        "SELL": ma_counter["SELL"],
        "NEUTRAL": ma_counter["NEUTRAL"],
        "COMPUTE": computed_ma
    }
    analysis.summary = {
        "RECOMMENDATION": recommend_summary,
        "BUY": oscillators_counter["BUY"] + ma_counter["BUY"],
        "SELL": oscillators_counter["SELL"] + ma_counter["SELL"],
        "NEUTRAL": oscillators_counter["NEUTRAL"] + ma_counter["NEUTRAL"]
    }
    
    return analysis


class TA_Handler:
    def __init__(self, screener: str, exchange: str, symbol: str, interval: str):
        self.screener = screener
        self.exchange = exchange
        self.symbol = symbol
        self.interval = interval
        self.indicators = TradingView.indicators.copy()
        
    def get_analysis(self) -> Analysis:
        """Fetch and compute analysis"""
        if not self.screener or not self.exchange or not self.symbol:
             raise ValueError("Screener, Exchange, and Symbol are required.")
             
        exchange_symbol = f"{self.exchange}:{self.symbol}"
        payload = TradingView.data([exchange_symbol], self.interval, self.indicators)
        
        scan_url = f"{TradingView.scan_url}{self.screener.lower()}/scan"
        
        try:
            res = TradingView.request("POST", scan_url, json=payload)
            res.raise_for_status()
            
            data = res.json()["data"]
            if not data:
                raise ValueError(f"No analysis data found for {exchange_symbol}")
                
            # data[0]["d"] 是指标值的数组
            result_values = data[0]["d"]
            
            # 映射为 dict
            indicators_val = {}
            for i, key in enumerate(self.indicators):
                 if i < len(result_values):
                     indicators_val[key] = result_values[i]
                     
            return calculate(
                indicators_val=indicators_val,
                indicators_key=self.indicators,
                screener=self.screener,
                symbol=self.symbol,
                exchange=self.exchange,
                interval=self.interval
            )
            
        except Exception as e:
            logger.error(f"TA_Handler get_analysis error: {e}")
            raise e

def get_multiple_analysis(screener: str, interval: str, symbols: List[str]) -> Dict[str, Analysis]:
    """Fetch multiple analysis"""
    if not screener or not symbols:
         raise ValueError("Screener and Symbols are required.")
         
    # 验证 format EXCHANGE:SYMBOL
    for s in symbols:
        if ":" not in s:
            raise ValueError(f"Invalid symbol format: {s}. Expected EXCHANGE:SYMBOL")
            
    payload = TradingView.data(symbols, interval, TradingView.indicators)
    scan_url = f"{TradingView.scan_url}{screener.lower()}/scan"
    
    final_results = {}
    
    try:
        res = TradingView.request("POST", scan_url, json=payload)
        res.raise_for_status()
        
        data = res.json()["data"]
        
        # data 是一个 list，每一项对应一个 symbol 的结果
        # item["s"] 是 "EXCHANGE:SYMBOL"
        # item["d"] 是 values array
        
        for item in data:
            symbol_key = item["s"]
            values = item["d"]
            
            # map to dict
            indicators_val = {}
            for i, key in enumerate(TradingView.indicators):
                if i < len(values):
                    indicators_val[key] = values[i]
            
            split_sym = symbol_key.split(":")
            exchange_name = split_sym[0]
            ticker_name = split_sym[1]
            
            analysis = calculate(
                indicators_val=indicators_val,
                indicators_key=TradingView.indicators,
                screener=screener,
                symbol=ticker_name,
                exchange=exchange_name,
                interval=interval
            )
            
            final_results[symbol_key] = analysis
            
        # 填充没有数据的 symbol 为 None
        for s in symbols:
            s_upper = s.upper()
            if s_upper not in final_results:
                final_results[s_upper] = None
                
        return final_results
        
    except Exception as e:
        logger.error(f"get_multiple_analysis error: {e}")
        raise e
