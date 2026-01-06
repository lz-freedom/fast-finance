import asyncio
import logging
from typing import List
import yfinance as yf
from yfinance import EquityQuery
from app.core.database import SQLiteManager

logger = logging.getLogger("fastapi")

class YahooSyncService:
    _is_running = False

    @classmethod
    def is_running(cls) -> bool:
        return cls._is_running

    @staticmethod
    async def sync_all_stocks():
        """
        全量同步所有定义的交易所股票数据到本地数据库。
        """
        if YahooSyncService._is_running:
            logger.warning("同步任务正在运行中，跳过本次请求。")
            return

        YahooSyncService._is_running = True
        logger.info("开始每日股票全量同步...")
        
        try:
            from app.core.constants import get_all_exchanges
            
            # 获取所有交易所配置
            exchanges_config = get_all_exchanges()
            
            total_new_all = 0
            total_processed_all = 0

            # 遍历每个交易所进行查询
            for ex in exchanges_config:
                region = ex.get("country_code", "").lower()
                exchange_code = ex.get("yahoo_exchange_code")
                acronym = ex.get("acronym")

                if not region or not exchange_code:
                    continue

                logger.info(f"正在同步交易所: {acronym} (Region: {region}, Code: {exchange_code})")
                
                offset = 0
                limit = 100
                
                while True:
                    try:
                        # 构造查询条件: 地区 + 交易所代码
                        query = EquityQuery("and", [
                            EquityQuery("eq", ["region", region]),
                            EquityQuery("is-in", ["exchange", exchange_code])
                        ])
                        
                        resp = await asyncio.to_thread(
                            yf.screen,
                            query,
                            size=limit,
                            sortField="dayvolume",
                            sortAsc=False,
                            offset=offset
                        )
                        
                        quotes = resp.get("quotes", [])
                        if not quotes:
                            # 当前交易所数据已取完
                            break
                        
                        # 打印批次日志
                        if quotes:
                            first_sym = quotes[0].get("symbol", "N/A")
                            last_sym = quotes[-1].get("symbol", "N/A")
                            logger.info(f"[{acronym}] 处理批次 Offset: {offset}, 数量: {len(quotes)}. 范围: {first_sym} - {last_sym}")

                        batch_stocks = []
                        
                        for q in quotes:
                            raw_symbol = q.get("symbol")
                            if not raw_symbol: continue
                            
                            # 1. 去掉后缀，只保留纯代码
                            # 例如 600036.SS -> 600036
                            symbol = raw_symbol.split(".")[0]
                            
                            # 2. 名称获取逻辑: shortName > displayName > prevName > symbol
                            name = q.get("shortName")
                            if not name: name = q.get("displayName")
                            if not name: name = q.get("prevName")
                            if not name: name = symbol
                            
                            # Normalize name (User request: fix all uppercase)
                            if name:
                                name = name.title()
                            
                            # 3. 构造 yahoo_stock 表所需数据
                            market_cap = q.get("marketCap", 0.0)
                            if market_cap is None: market_cap = 0.0
                            
                            currency = q.get("currency", "")
                            
                            # Calculate Market Cap USD
                            usd_rate = ex.get("usd_rate", 1.0)
                            market_cap_usd = float(market_cap) * float(usd_rate)

                            batch_stocks.append({
                                "yahoo_stock_symbol": raw_symbol,
                                "yahoo_exchange_symbol": exchange_code,
                                "stock_symbol": symbol,
                                "exchange_acronym": acronym,
                                "name": name,
                                "currency": currency,
                                "market_cap": str(market_cap),
                                "market_cap_usd": str(market_cap_usd)
                            })
                        
                        # 批量写入数据库 (yahoo_stock)
                        if batch_stocks:
                            count = SQLiteManager.upsert_yahoo_stock_batch(batch_stocks)
                            total_new_all += count # upsert_yahoo_stock_batch returns total count, assuming all are "new/updated"
                            # stats logic might need adjustment but for now just sum up
                            total_processed_all += len(batch_stocks)
                        
                        offset += limit
                        
                        # 安全保险：防止单个交易所数据量也过大导致的死循环
                        if offset > 100000:
                            logger.warning(f"[{acronym}] 达到单交易所 100,000 条限制，停止该交易所同步。")
                            break
                            
                        # 小睡一下避免请求过快
                        await asyncio.sleep(0.5)
                        
                    except Exception as e:
                        logger.error(f"同步 [{acronym}] 时出错 (Offset {offset}): {e}")
                        break
            
            logger.info(f"股票全量同步完成。总处理: {total_processed_all}, 新增: {total_new_all}")
        finally:
            YahooSyncService._is_running = False
