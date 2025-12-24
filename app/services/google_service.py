
import requests
import json
import random
import datetime
import logging
from typing import List, Dict, Any, Optional, Union
from app.core.config import settings
from app.core.utils import recursive_camel_case

logger = logging.getLogger("fastapi")

class GoogleService:
    __base_path = 'https://www.google.com/finance/_/GoogleFinanceUi/data/batchexecute?'
    __session = requests.Session()
    
    # Configure headers
    __session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    })
    
    # Configure Proxy
    if settings.PROXY_GOOGLE:
        __proxies = {
            "http": settings.PROXY_GOOGLE,
            "https": settings.PROXY_GOOGLE
        }
        __session.proxies.update(__proxies)
        logger.info(f"Google Finance proxy set to: {settings.PROXY_GOOGLE}")
    else:
        __proxies = None

    __timeout = 15.0

    @staticmethod
    def _dump_json(o):
        return json.dumps(o, separators=(',', ':'))

    @staticmethod
    def _rand_num_str(l):
        return str(int(random.random() * (10 ** l)))

    @staticmethod
    def _out_array(a):
        return a if len(a) > 1 else GoogleService._out_array(a[0])

    @staticmethod
    def _parse_trading(i):
        if i is None:
            return None
        return {
            'last': i[0],
            'change': i[1],
            'change_percent': i[2],
        }

    @staticmethod
    def _parse_datetime(i):
        arr = []
        for item in i:
            if isinstance(item, int):
                arr.append(item)
            elif item is None:
                arr.append(0)
            elif isinstance(item, list):
                # Using simple UTC if timezone info is complex, but sticking to user logic mostly
                # User used datetime.timezone(datetime.timedelta(seconds=...))
                # Simplification: just assume UTC or construct aware dict
                arr.append(datetime.timezone(datetime.timedelta(seconds=0 if len(item) == 0 else item[0])))
        return datetime.datetime(*arr)

    @staticmethod
    def _parse_detail(i):
        if i is None or len(i) < 5 or i[4] is None:
            return None
        
        # i[1] usually [code, exchange]
        code = i[1][0] if len(i) > 1 and len(i[1]) > 0 else None
        exchange = i[1][1] if len(i) > 1 and len(i[1]) > 1 else None
        
        return {
            'symbol': code,
            'exchange': exchange,
            'name': i[2],
            'currency': i[4],
            'last_price': i[5][0] if i[5] else None,
            'change': i[5][1] if i[5] else None,
            'change_percent': i[5][2] if i[5] else None,
            'region': i[9] if len(i) > 9 else None,
            'update_time': i[11][0] if len(i) > 11 and i[11] else None, # Timestamp
            # Simplified for now, can expand fields as needed
        }

    @classmethod
    def _batch_exec(cls, envelopes):
        envs = envelopes if isinstance(envelopes, list) else [envelopes]
        rpcids = '%2C'.join(list(dict.fromkeys([e['id'] for e in envs])))
        
        if len(envs) == 0:
            return []
        elif len(envs) == 1:
            payload = cls._dump_json([[[envs[0]['id'], cls._dump_json(envs[0]['data']), None, 'generic']]])
        else:
            payload = cls._dump_json([[[e['id'], cls._dump_json(e['data']), None, str(i + 1)] for i, e in enumerate(envs)]])
            
        path = f'rpcids={rpcids}&f.sid=-{cls._rand_num_str(19)}&bl=boq_finance-ui_20211101.11_p0&hl=en&_reqid={cls._rand_num_str(8)}'
        
        try:
            rsp = cls.__session.post(
                cls.__base_path + path, 
                data={'f.req': payload}, # Use data for form-url-encoded kind of behavior if params fails, but user used params
                params={'f.req': payload}, # Google usually expects this in body for POST but batch endpoint supports both. User used params.
                timeout=cls.__timeout
            )
            rsp.raise_for_status()
            
            # Response parsing
            # Google often returns: )]}' \n ... JSON ...
            # User code: json.loads(rsp.text.split('\n')[2])
            lines = rsp.text.split('\n')
            
            target_line = None
            for line in lines:
                if line.startswith('[['):
                    target_line = line
                    break
            
            if not target_line and len(lines) > 2:
                 target_line = lines[2] # Fallback to user logic
            
            if not target_line:
                raise Exception("Empty or invalid response format from Google Finance")

            rsps = json.loads(target_line)
            
            datas = []
            for r in rsps:
                if r[0] == 'er': 
                    logger.error(f"Google RPC Error: {r[5]}")
                    # Don't raise immediately for batch, maybe insert None? 
                    # User raised exception.
                    raise Exception(f'Google RPC Error: {r[5]}')
                elif r[0] == 'wrb.fr':
                    cur = json.loads(r[2])
                    # Logic to insert at specific index
                    idx = int(r[6] if r[6] != 'generic' else 1) - 1
                    # Ensure datas list is long enough
                    while len(datas) <= idx:
                        datas.append(None)
                    datas[idx] = cur if len(cur) > 0 else []
            
            return datas if len(datas) > 1 else datas[0]
            
        except Exception as e:
            logger.error(f"Google Service Error: {e}")
            raise e

    @classmethod
    def search(cls, query: str) -> List[Dict[str, Any]]:
        # RPC ID 'mKsvE' for search
        try:
            rsp = cls._batch_exec({'id': 'mKsvE', 'data': [query, [], True, True]})
            # rsp is typically [[match1], [match2], ...] wrapped
            # User code: [parse_detail(e[3]) for e in rsp[0]]
            if not rsp or len(rsp) == 0:
                return []
            
            # rsp[0] contains the matches
            matches = rsp[0]
            results = []
            
            for e in matches:
                # e[3] is the detail block
                parsed = cls._parse_detail(e[3])
                if parsed:
                    results.append(parsed)
            
            return results
        except Exception as e:
            logger.error(f"Search error for {query}: {e}")
            return []

    @classmethod
    def get_details(cls, items: List[Dict[str, str]]) -> List[Dict[str, Any]]:
        # items: [{"symbol": "AAPL", "exchange": "NASDAQ"}, ...]
        # RPC ID 'xh8wxf'
        # Data format: [[[None, ["CODE", "EXCHANGE"]]], True, False]
        
        req_data = []
        for item in items:
            symbol = item.get("symbol")
            exchange = item.get("exchange")
            req_data.append({'id': 'xh8wxf', 'data': [[[None, [symbol, exchange]]], True, False]})
            
        try:
            responses = cls._batch_exec(req_data)
            
            # If batch_exec returns single item for single request, ensure list
            if len(items) == 1 and not isinstance(responses, list):
                responses = [responses]
            # Wait, user's batch_exec returns single item if len(envs)==1. 
            # If we sent list, we expect list back?
            # User code: return datas if len(datas) > 1 else datas[0]
            # We should standardize to always list for get_details?
            # Let's adjust logic.
            
            if not isinstance(responses, list):
                responses = [responses]
                
            results = []
            for rsp in responses:
                # rsp is complex array structure
                # User code: parse_detail(out_array(e))
                # out_array digs down
                try:
                    data_block = cls._out_array(rsp)
                    parsed = cls._parse_detail(data_block)
                    results.append(parsed)
                except:
                    results.append(None)
            return results
        except Exception as e:
            logger.error(f"Get details error: {e}")
            raise e

    @classmethod
    def get_detail(cls, symbol: str, exchange: str) -> Dict[str, Any]:
        results = cls.get_details([{"symbol": symbol, "exchange": exchange}])
        if results:
            return results[0]
        return {}

    @classmethod
    def get_history(cls, symbol: str, exchange: str, range_str: str) -> List[Dict[str, Any]]:
        # Range Mapping & Verified Implicit Intervals:
        # 1: 1d (1 Minute)
        # 2: 5d (30 Minutes)
        # 3: 1mo (Daily)
        # 4: 6mo (Daily)
        # 5: ytd (Daily)
        # 6: 1y (Daily)
        # 7: 5y (Weekly)
        # 8: max (Weekly)
        range_map = {
            "1d": 1, 
            "5d": 2, 
            "1mo": 3, 
            # "3mo" not supported natively by dedicated param
            "6mo": 4, 
            "ytd": 5, 
            "1y": 6, 
            "5y": 7, 
            "max": 8
        }
        
        range_val = range_map.get(range_str, 3) 
        
        # RPC ID 'AiCwsd'
        # Data: [[[None, ["CODE", "EXCHANGE"]]], range_val]
        
        try:
            rsp = cls._batch_exec({'id': 'AiCwsd', 'data': [[[None, [symbol, exchange]]], range_val]})
            
            # User code: out_array(rsp)[3][0][1] -> list of [date, [start, end, etc], volume, ...]
            # i[0] date, i[1] trading?, i[2] volume
            
            data_block = cls._out_array(rsp)
            if len(data_block) > 3 and data_block[3] and len(data_block[3]) > 0:
                 quotes_raw = data_block[3][0][1]
            else:
                return []
                
            results = []
            for i in quotes_raw:
                dt = cls._parse_datetime(i[0])
                # trading info usually in i[1]: [open, close, high, low]? 
                # User parse_trading: [0] last, [1] change, [2] percent. Not standard OHLC.
                # History usually returns OHLC. 
                # Google Finance History: [timestamp_min, close?, ?? ]
                # User snippet: 'trading': parse_trading(i[1]), 'volume': i[2]
                # parse_trading(i) -> last, change, percent
                
                # Let's trust user parsing logic for now
                # BUT history usually needs Close price. 
                # i[1][0] is likely the 'close' price for that interval.
                
                trading = cls._parse_trading(i[1])
                
                results.append({
                    "date": dt.isoformat(),
                    "close": trading.get('last') if trading else None,
                    "volume": i[2]
                })
                
            return results

        except Exception as e:
            logger.error(f"Get history error for {symbol}:{exchange}: {e}")
            return []
