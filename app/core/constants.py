from typing import List, Dict, Optional

# 平台常量
PLATFORM_YAHOO = "yahoo"
PLATFORM_INVESTING = "investing"
PLATFORM_GOOGLE = "google"
PLATFORM_TRADINGVIEW = "tradingview"

# 映射数据
# 包含列: id, country_id, acronym, yahoo_stock_symbol_suffix, investing_code, google_code, yahoo_exchange_code
EXCHANGE_MAPPING: List[Dict[str, str]] = [
    {"acronym": "SSE", "yahoo_stock_symbol_suffix": "SS", "investing_code": "Shanghai", "google_code": "SHA", "country_code": "cn", "yahoo_exchange_code": "SHH"},
    {"acronym": "SZSE", "yahoo_stock_symbol_suffix": "SZ", "investing_code": "Shenzhen", "google_code": "SHE", "country_code": "cn", "yahoo_exchange_code": "SHZ"},
    {"acronym": "HKEX", "yahoo_stock_symbol_suffix": "HK", "investing_code": "Hong Kong", "google_code": "HKG", "country_code": "hk", "yahoo_exchange_code": "HKG"},
    {"acronym": "NYSE", "yahoo_stock_symbol_suffix": "", "investing_code": "NYSE", "google_code": "NYSE", "country_code": "us", "yahoo_exchange_code": "NYQ"},
    {"acronym": "NASDAQ", "yahoo_stock_symbol_suffix": "", "investing_code": "NASDAQ", "google_code": "NASDAQ", "country_code": "us", "yahoo_exchange_code": "NMS"},
    {"acronym": "SGX", "yahoo_stock_symbol_suffix": "SI", "investing_code": "Singapore", "google_code": "SGX", "country_code": "sg", "yahoo_exchange_code": "SES"},
    {"acronym": "TSE", "yahoo_stock_symbol_suffix": "T", "investing_code": "Tokyo", "google_code": "TYO", "country_code": "jp", "yahoo_exchange_code": "JPX"},
    {"acronym": "NSE", "yahoo_stock_symbol_suffix": "NS", "investing_code": "NSE", "google_code": "NSE", "country_code": "in", "yahoo_exchange_code": "NSI"},
    {"acronym": "LSE", "yahoo_stock_symbol_suffix": "L", "investing_code": "London", "google_code": "LON", "country_code": "uk", "yahoo_exchange_code": "LSE"},
    {"acronym": "TSX", "yahoo_stock_symbol_suffix": "TO", "investing_code": "Toronto", "google_code": "TSE", "country_code": "ca", "yahoo_exchange_code": "TOR"},
    {"acronym": "TSXV", "yahoo_stock_symbol_suffix": "V", "investing_code": "TSXV", "google_code": "CVE", "country_code": "ca", "yahoo_exchange_code": "VAN"},
    {"acronym": "ASX", "yahoo_stock_symbol_suffix": "AX", "investing_code": "Sydney", "google_code": "ASX", "country_code": "au", "yahoo_exchange_code": "ASX"},
]

def get_exchange_info_by_acronym(acronym: str) -> Optional[Dict[str, str]]:
    """
    根据缩写获取交易所映射信息。
    不区分大小写。
    """
    acronym_upper = acronym.upper()
    return next((item for item in EXCHANGE_MAPPING if item["acronym"] == acronym_upper), None)

def get_exchange_info_by_platform_code(platform: str, code: str) -> Optional[Dict[str, str]]:
    """
    根据平台代码获取交易所映射信息（反向查找）。
    
    参数:
        platform: 'yahoo', 'investing', 'google', 'tradingview'
        code: 该平台使用的代码 (例如 'SZ', 'Shenzhen', 'SHE', 'SZSE')
    """
    platform = platform.lower()
    key_map = {
        PLATFORM_YAHOO: "yahoo_stock_symbol_suffix",
        PLATFORM_INVESTING: "investing_code",
        PLATFORM_GOOGLE: "google_code",
        PLATFORM_TRADINGVIEW: "acronym" 
    }
    
    target_key = key_map.get(platform)
    if not target_key:
        return None
    
    # 检查精确匹配或不区分大小写的匹配
    for item in EXCHANGE_MAPPING:
        if item.get(target_key) == code:
            return item
            
    # 回退到不区分大小写的匹配
    code_lower = code.lower()
    for item in EXCHANGE_MAPPING:
        if str(item.get(target_key, "")).lower() == code_lower:
            return item

    # 特殊处理 Yahoo Screen Code (如 SHH, SHZ)
    if platform == PLATFORM_YAHOO:
        for item in EXCHANGE_MAPPING:
            if item.get("yahoo_exchange_code") == code:
                return item

    return None

def get_exchanges_by_country(country_code: str) -> List[Dict[str, str]]:
    """
    获取指定国家代码的所有交易所。
    """
    country_code_lower = country_code.lower()
    return [item for item in EXCHANGE_MAPPING if item.get("country_code", "").lower() == country_code_lower]

def get_all_exchanges() -> List[Dict[str, str]]:
    """
    获取所有可用的交易所映射。
    """
    return EXCHANGE_MAPPING

def get_all_acronyms() -> List[str]:
    """
    获取所有支持的交易所缩写列表。
    """
    return [item["acronym"] for item in EXCHANGE_MAPPING]

def get_yahoo_screen_exchanges() -> List[str]:
    """
    获取用于Yahoo Screener的交易所代码列表 (例如 ['SHH', 'SHZ', ...])
    """
    return [item["yahoo_exchange_code"] for item in EXCHANGE_MAPPING if item.get("yahoo_exchange_code")]

def get_yahoo_screen_mapping() -> Dict[str, str]:
    """
    获取 Yahoo Screen Code 到 系统Acronym 的映射 (例如 {'SHH': 'SSE', ...})
    """
    return {item["yahoo_exchange_code"]: item["acronym"] for item in EXCHANGE_MAPPING if item.get("yahoo_exchange_code")}

def get_stock_info(stock_symbol: str, exchange_acronym: str, platform: str) -> Optional[Dict[str, str]]:
    """
    获取特定平台的格式化股票信息。
    
    参数:
        stock_symbol: 股票代码 (例如 000001)
        exchange_acronym: 交易所缩写 (例如 SZSE)
        platform: 目标平台 ('yahoo', 'investing', 'google', 'tradingview')
        
    返回:
        包含以下内容的字典:
            - stock_symbol: 平台格式化的股票代码
            - stock_symbol_source: 原始输入股票代码
            - exchange_acronym: 输入的交易所缩写
            - exchange_code: 平台特定的交易所代码
            - country_code: 国家代码
    """
    mapping = get_exchange_info_by_acronym(exchange_acronym)
    if not mapping:
        return None
        
    result = {
        "stock_symbol_source": stock_symbol,
        "exchange_acronym": exchange_acronym,
        "country_code": mapping.get("country_code", ""),
        "stock_symbol": "",
        "exchange_code": ""
    }
    
    platform = platform.lower()
    
    if platform == PLATFORM_YAHOO:
        suffix = mapping.get("yahoo_stock_symbol_suffix", "")
        result["exchange_code"] = suffix
        result["stock_symbol"] = f"{stock_symbol}.{suffix}" if suffix else stock_symbol
        
    elif platform == PLATFORM_INVESTING:
        code = mapping.get("investing_code", "")
        result["exchange_code"] = code
        result["stock_symbol"] = stock_symbol
        
    elif platform == PLATFORM_GOOGLE:
        code = mapping.get("google_code", "")
        result["exchange_code"] = code
        result["stock_symbol"] = stock_symbol
        
    elif platform == PLATFORM_TRADINGVIEW:
        code = mapping.get("acronym", "")
        result["exchange_code"] = code
        result["stock_symbol"] = stock_symbol # TradingView 通常在其他地方只使用 Symbol + Exchange Code
        
    else:
        return None
        
    return result
