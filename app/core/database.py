import pymysql
import os
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from app.core.config import settings

logger = logging.getLogger("fastapi")

class LoggingCursor(pymysql.cursors.DictCursor):
    def execute(self, query, args=None):
        if args:
            log_query = f"{query} % {args}"
        else:
            log_query = query
        logger.info(f"[SQL] {log_query}")
        return super().execute(query, args)

    def executemany(self, query, args):
        logger.info(f"[SQL] [Msg: batch execution of {len(args) if args else 0} rows] {query}")
        return super().executemany(query, args)

class DBManager:
    @staticmethod
    def get_connection():
        return pymysql.connect(
            host=settings.MYSQL_SERVER,
            port=settings.MYSQL_PORT,
            user=settings.MYSQL_USER,
            password=settings.MYSQL_PASSWORD,
            database=settings.MYSQL_DB,
            charset='utf8mb4',
            cursorclass=LoggingCursor,
            autocommit=False,
            init_command='SET time_zone = "+08:00"'
        )

    @staticmethod
    def init_db():
        """
        Initialize the database and create tables if they don't exist.
        """
        try:
            conn = DBManager.get_connection()
            cursor = conn.cursor()
            
            # fast_finance_stocks REMOVED as requested
            
            # Create tradingview_stock table
            DBManager.init_tradingview_table(cursor)
            
            # Create investing_stock table
            DBManager.init_investing_table(cursor)
            
            # Create stock_history_cache table
            DBManager.init_history_cache_table(cursor)

            # Create yahoo_analysis_cache table
            DBManager.init_analysis_cache_table(cursor)
            
            # Create yahoo_stock table
            DBManager.init_yahoo_stock_table(cursor)

            # Create yahoo_stock_related_cache table
            DBManager.init_yahoo_stock_related_cache_table(cursor)

            # Create job_execution_logs table
            DBManager.init_job_log_table(cursor)
            
            conn.commit()
            conn.close()
            logger.info(f"Database initialized at {settings.MYSQL_SERVER}:{settings.MYSQL_PORT}/{settings.MYSQL_DB}")
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")

    # --- Job Logging Methods ---

    @staticmethod
    def init_job_log_table(conn_or_cursor=None):
        """
        Create job_execution_logs table.
        """
        close_conn = False
        conn = None
        if conn_or_cursor is None:
            conn = DBManager.get_connection()
            cursor = conn.cursor()
            close_conn = True
        else:
            if hasattr(conn_or_cursor, 'execute'):
                cursor = conn_or_cursor
            else:
                cursor = conn_or_cursor.cursor()

        try:
            # Drop old table to enforce new schema if needed (Standardization)
            # cursor.execute("DROP TABLE IF EXISTS fast_finance_job_execution_logs")
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS fast_finance_job_execution_logs (
                    id BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY COMMENT '任务日志ID',
                    job_id VARCHAR(100),
                    job_name VARCHAR(255),
                    status VARCHAR(50), 
                    start_time DATETIME,
                    end_time DATETIME,
                    duration_seconds DECIMAL(10, 2),
                    message TEXT,
                    create_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
                    update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '修改时间'
                )
            """)
            if close_conn:
                conn.commit()
        except Exception as e:
            logger.error(f"Failed to create job_execution_logs table: {e}")
        finally:
            if close_conn and conn:
                conn.close()

    @staticmethod
    def log_job_start(job_id: str, job_name: str) -> int:
        try:
            conn = DBManager.get_connection()
            cursor = conn.cursor()
            now = datetime.now()
            
            cursor.execute("""
                INSERT INTO fast_finance_job_execution_logs (job_id, job_name, status, start_time)
                VALUES (%s, %s, 'RUNNING', %s)
            """, (job_id, job_name, now))
            
            row_id = cursor.lastrowid
            conn.commit()
            conn.close()
            return row_id
        except Exception as e:
            logger.error(f"Error logging job start: {e}")
            return -1

    @staticmethod
    def log_job_finish(log_id: int, status: str, message: str = ""):
        if log_id < 0:
            return
            
        try:
            conn = DBManager.get_connection()
            cursor = conn.cursor()
            now = datetime.now()
            
            cursor.execute("SELECT start_time FROM fast_finance_job_execution_logs WHERE id = %s", (log_id,))
            row = cursor.fetchone()
            start_time = None
            if row:
                if isinstance(row['start_time'], str): 
                    try:
                        start_time = datetime.fromisoformat(row['start_time'])
                    except:
                        pass
                else:
                    start_time = row['start_time']
            
            duration = 0.0
            if start_time:
                duration = (now - start_time).total_seconds()
            
            cursor.execute("""
                UPDATE fast_finance_job_execution_logs 
                SET status = %s, end_time = %s, duration_seconds = %s, message = %s
                WHERE id = %s
            """, (status, now, duration, message, log_id))
            
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"Error logging job finish: {e}")

    @staticmethod
    def get_job_logs(limit: int = 50) -> List[Dict[str, Any]]:
        try:
            conn = DBManager.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM fast_finance_job_execution_logs ORDER BY id DESC LIMIT %s", (limit,))
            rows = cursor.fetchall()
            conn.close()
            return rows
        except Exception as e:
            logger.error(f"Error getting job logs: {e}")
            return []

    # --- TradingView Sync Methods ---

    @staticmethod
    def init_tradingview_table(conn_or_cursor=None):
        close_conn = False
        conn = None
        if conn_or_cursor is None:
            conn = DBManager.get_connection()
            cursor = conn.cursor()
            close_conn = True
        else:
            if hasattr(conn_or_cursor, 'execute'):
                cursor = conn_or_cursor
            else:
                cursor = conn_or_cursor.cursor()

        try:
            # We must DROP TABLE to enforce new schema if exists
            # WARNING: This deletes data!
            # Since user requested strict schema changes and it's dev, we proceed.
            # cursor.execute("DROP TABLE IF EXISTS fast_finance_tradingview_stock")

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS fast_finance_tradingview_stock (
                    id BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY COMMENT 'ID',
                    tradingview_full_stock_symbol VARCHAR(100) UNIQUE NOT NULL,
                    stock_symbol VARCHAR(50),
                    exchange_acronym VARCHAR(20),
                    name VARCHAR(255),
                    description TEXT,
                    logoid VARCHAR(1000),
                    logo_url VARCHAR(1000),
                    
                    ipo_offer_date DATE,
                    ipo_offer_price DECIMAL(38, 18),
                    ipo_deal_amount DECIMAL(38, 18),
                    sector_tr VARCHAR(255),
                    sector VARCHAR(255),
                    
                    create_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
                    update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '修改时间'
                )
            """)
            
            if close_conn:
                conn.commit()
        except Exception as e:
            logger.error(f"Failed to create tradingview_stock table: {e}")
        finally:
            if close_conn and conn:
                conn.close()

    @staticmethod
    def init_investing_table(conn_or_cursor=None):
        close_conn = False
        conn = None
        if conn_or_cursor is None:
            conn = DBManager.get_connection()
            cursor = conn.cursor()
            close_conn = True
        else:
            if hasattr(conn_or_cursor, 'execute'):
                cursor = conn_or_cursor
            else:
                cursor = conn_or_cursor.cursor()

        try:
            # DROP TABLE to enforce new schema
            # cursor.execute("DROP TABLE IF EXISTS fast_finance_investing_stock")

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS fast_finance_investing_stock (
                    id BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY COMMENT 'ID',
                    investing_stock_pair_id BIGINT UNIQUE NOT NULL,
                    investing_stock_uid VARCHAR(100),
                    -- Removed tradingview_full_stock_symbol as requested
                    stock_symbol VARCHAR(50),
                    exchange_acronym VARCHAR(20),
                    logo_url VARCHAR(255),
                    
                    name_cn VARCHAR(255),
                    name_en VARCHAR(255),
                    investing_sector_cn VARCHAR(255),
                    investing_sector_en VARCHAR(255),
                    investing_industry_cn VARCHAR(255),
                    investing_industry_en VARCHAR(255),
                    
                    create_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
                    update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '修改时间'
                )
            """)
            
            if close_conn:
                conn.commit()
        except Exception as e:
            logger.error(f"Failed to create investing_stock table: {e}")
        finally:
            if close_conn and conn:
                conn.close()

    @staticmethod
    def upsert_tradingview_batch(items: List[Dict[str, Any]]) -> int:
        if not items:
            return 0
            
        try:
            conn = DBManager.get_connection()
            cursor = conn.cursor()
            
            db_rows = []
            for item in items:
                # Construct URL if logoid present
                logoid = item.get('logoid', '')
                logo_url = f"https://s3-symbol-logo.tradingview.com/{logoid}.svg" if logoid else ""
                
                # Handle DATE logic for ipo_offer_date
                # Should be valid DATE string (YYYY-MM-DD) or None
                ipo_date = item.get('ipo_offer_date')
                if not ipo_date:
                    ipo_date = None
                
                db_rows.append((
                   item['tradingview_full_stock_symbol'],
                   item.get('stock_symbol', ''),
                   item.get('exchange_acronym', ''),
                   item.get('name', ''),
                   item.get('description', ''),
                   logoid,
                   logo_url,
                   
                   ipo_date,
                   item.get('ipo_offer_price'),
                   item.get('ipo_deal_amount'),
                   item.get('sector_tr'),
                   item.get('sector')
                ))

            # No created_at, updated_at passed
            sql = """
                INSERT INTO fast_finance_tradingview_stock (
                    tradingview_full_stock_symbol, stock_symbol, exchange_acronym, name, 
                    description, logoid, logo_url, 
                    ipo_offer_date, ipo_offer_price, ipo_deal_amount, sector_tr, sector
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    stock_symbol=VALUES(stock_symbol),
                    exchange_acronym=VALUES(exchange_acronym),
                    name=VALUES(name),
                    description=VALUES(description),
                    logoid=VALUES(logoid),
                    logo_url=VALUES(logo_url),
                    ipo_offer_date=VALUES(ipo_offer_date),
                    ipo_offer_price=VALUES(ipo_offer_price),
                    ipo_deal_amount=VALUES(ipo_deal_amount),
                    sector_tr=VALUES(sector_tr),
                    sector=VALUES(sector)
            """
            cursor.executemany(sql, db_rows)
            
            conn.commit()
            count = cursor.rowcount
            conn.close()
            return len(items) 
        except Exception as e:
            logger.error(f"Error upserting tradingview batch: {e}")
            return 0

    @staticmethod
    def get_tradingview_stocks(exchange_acronym: Optional[str] = None, 
                               min_created_at: Optional[datetime] = None) -> List[Dict[str, Any]]:
        try:
            conn = DBManager.get_connection()
            cursor = conn.cursor()
            
            query = "SELECT * FROM fast_finance_tradingview_stock WHERE 1=1"
            params = []
            
            if exchange_acronym:
                query += " AND exchange_acronym = %s"
                params.append(exchange_acronym)
            
            if min_created_at:
                query += " AND create_time >= %s"
                params.append(min_created_at)
                
            cursor.execute(query, tuple(params))
            rows = cursor.fetchall()
            conn.close()
            return rows
        except Exception as e:
            logger.error(f"Error fetching tradingview stocks: {e}")
            return []

    @staticmethod
    def cleanup_tradingview_duplicates() -> int:
        try:
            conn = DBManager.get_connection()
            cursor = conn.cursor()
            
            sql = """
            DELETE t1 
            FROM fast_finance_tradingview_stock t1
            JOIN fast_finance_tradingview_stock t2 
              ON (t2.tradingview_full_stock_symbol = REPLACE(t1.tradingview_full_stock_symbol, '.U', '.UN') 
                  OR t2.tradingview_full_stock_symbol = REPLACE(t1.tradingview_full_stock_symbol, '.U', '.UM'))
            WHERE t1.tradingview_full_stock_symbol LIKE '%.U'
            """
            
            cursor.execute(sql)
            count = cursor.rowcount
            
            conn.commit()
            conn.close()
            
            if count > 0:
                logger.info(f"Cleaned up {count} duplicate TradingView stocks ending in .U")
                
            return count
        except Exception as e:
            logger.error(f"Error cleaning up duplicates: {e}")
            return 0

    @staticmethod
    def upsert_investing_batch(items: List[Dict[str, Any]]) -> int:
        if not items:
            return 0
            
        try:
            conn = DBManager.get_connection()
            cursor = conn.cursor()
            
            db_rows = []
            for item in items:
                db_rows.append((
                   item['investing_stock_pair_id'],
                   item.get('investing_stock_uid', ''),
                   # No tradingview_full_stock_symbol
                   item.get('stock_symbol', ''),
                   item.get('exchange_acronym', ''),
                   item.get('logo_url', ''),
                   
                   item.get('name_cn'),
                   item.get('name_en'),
                   item.get('investing_sector_cn'),
                   item.get('investing_sector_en'),
                   item.get('investing_industry_cn'),
                   item.get('investing_industry_en')
                ))

            sql = """
                INSERT INTO fast_finance_investing_stock (
                    investing_stock_pair_id, investing_stock_uid,
                    stock_symbol, exchange_acronym, logo_url,
                    name_cn, name_en, 
                    investing_sector_cn, investing_sector_en,
                    investing_industry_cn, investing_industry_en
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    investing_stock_uid=VALUES(investing_stock_uid),
                    stock_symbol=VALUES(stock_symbol),
                    exchange_acronym=VALUES(exchange_acronym),
                    logo_url=VALUES(logo_url),
                    
                    name_cn=COALESCE(VALUES(name_cn), name_cn),
                    name_en=COALESCE(VALUES(name_en), name_en),
                    investing_sector_cn=COALESCE(VALUES(investing_sector_cn), investing_sector_cn),
                    investing_sector_en=COALESCE(VALUES(investing_sector_en), investing_sector_en),
                    investing_industry_cn=COALESCE(VALUES(investing_industry_cn), investing_industry_cn),
                    investing_industry_en=COALESCE(VALUES(investing_industry_en), investing_industry_en)
            """
            
            cursor.executemany(sql, db_rows)
            
            conn.commit()
            count = cursor.rowcount
            conn.close()
            return len(items)
        except Exception as e:
            logger.error(f"Error upserting investing batch: {e}")
            return 0

    @staticmethod
    def get_investing_stocks(exchange_acronym: Optional[str] = None, min_created_at: Optional[datetime] = None) -> List[Dict[str, Any]]:
        try:
            conn = DBManager.get_connection()
            cursor = conn.cursor()
            
            query = "SELECT * FROM fast_finance_investing_stock WHERE 1=1"
            params = []
            
            if exchange_acronym:
                query += " AND exchange_acronym = %s"
                params.append(exchange_acronym)
                
            if min_created_at:
                query += " AND create_time >= %s"
                params.append(min_created_at)
                
            cursor.execute(query, tuple(params))
            rows = cursor.fetchall()
            conn.close()
            return rows
        except Exception as e:
            logger.error(f"Error fetching investing stocks: {e}")
            return []

    # --- History Cache Methods ---

    @staticmethod
    def init_history_cache_table(conn_or_cursor=None):
        close_conn = False
        conn = None
        if conn_or_cursor is None:
            conn = DBManager.get_connection()
            cursor = conn.cursor()
            close_conn = True
        else:
            if hasattr(conn_or_cursor, 'execute'):
                cursor = conn_or_cursor
            else:
                cursor = conn_or_cursor.cursor()

        try:
            # DROP TABLE if schema changed (it did, adding id, times)
            # cursor.execute("DROP TABLE IF EXISTS fast_finance_stock_history_cache")

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS fast_finance_stock_history_cache (
                    id BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
                    cache_key VARCHAR(255) UNIQUE NOT NULL,
                    data LONGTEXT,
                    create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
                    update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                )
            """)
            if close_conn:
                conn.commit()
        except Exception as e:
            logger.error(f"Failed to create stock_history_cache table: {e}")
        finally:
            if close_conn and conn:
                conn.close()

    @staticmethod
    def get_history_cache(cache_key: str) -> Optional[str]:
        try:
            conn = DBManager.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT data FROM fast_finance_stock_history_cache WHERE cache_key = %s", (cache_key,))
            row = cursor.fetchone()
            conn.close()
            return row['data'] if row else None
        except Exception as e:
            logger.error(f"Error getting history cache: {e}")
            return None

    @staticmethod
    def upsert_history_cache(cache_key: str, data: str):
        try:
            conn = DBManager.get_connection()
            cursor = conn.cursor()
            
            # Use INSERT ON DUPLICATE to handle timestamps properly (REPLACE creates new row, resetting create_time)
            cursor.execute("""
                INSERT INTO fast_finance_stock_history_cache (cache_key, data)
                VALUES (%s, %s)
                ON DUPLICATE KEY UPDATE
                    data=VALUES(data)
            """, (cache_key, data))
            
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"Error upserting history cache: {e}")

    # --- Analysis Cache Methods ---

    @staticmethod
    def init_analysis_cache_table(conn_or_cursor=None):
        close_conn = False
        conn = None
        if conn_or_cursor is None:
            conn = DBManager.get_connection()
            cursor = conn.cursor()
            close_conn = True
        else:
            if hasattr(conn_or_cursor, 'execute'):
                cursor = conn_or_cursor
            else:
                cursor = conn_or_cursor.cursor()

        try:
            # cursor.execute("DROP TABLE IF EXISTS fast_finance_yahoo_analysis_cache")
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS fast_finance_yahoo_analysis_cache (
                    id BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
                    symbol VARCHAR(50) UNIQUE NOT NULL,
                    data LONGTEXT,
                    create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
                    update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                )
            """)
            if close_conn:
                conn.commit()
        except Exception as e:
            logger.error(f"Failed to create yahoo_analysis_cache table: {e}")
        finally:
            if close_conn and conn:
                conn.close()

    @staticmethod
    def get_analysis_cache(symbol: str) -> Optional[Dict[str, Any]]:
        try:
            conn = DBManager.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT data, create_time FROM fast_finance_yahoo_analysis_cache WHERE symbol = %s", (symbol,))
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return {
                    "data": row["data"],
                    "created_at": row["create_time"] # Map back to expected key in app? Or fix app
                }
            return None
        except Exception as e:
            logger.error(f"Error getting analysis cache for {symbol}: {e}")
            return None

    @staticmethod
    def upsert_analysis_cache(symbol: str, data: str):
        try:
            conn = DBManager.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO fast_finance_yahoo_analysis_cache (symbol, data)
                VALUES (%s, %s)
                ON DUPLICATE KEY UPDATE data=VALUES(data)
            """, (symbol, data))
            
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"Error upserting analysis cache for {symbol}: {e}")

    @staticmethod
    def init_yahoo_stock_table(conn_or_cursor=None):
        close_conn = False
        conn = None
        if conn_or_cursor is None:
            conn = DBManager.get_connection()
            cursor = conn.cursor()
            close_conn = True
        else:
            if hasattr(conn_or_cursor, 'execute'):
                cursor = conn_or_cursor
            else:
                cursor = conn_or_cursor.cursor()

        try:
            # cursor.execute("DROP TABLE IF EXISTS fast_finance_yahoo_stock")
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS fast_finance_yahoo_stock (
                    id BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY COMMENT 'ID',
                    yahoo_stock_symbol VARCHAR(50) UNIQUE NOT NULL,
                    yahoo_exchange_symbol VARCHAR(20),
                    stock_symbol VARCHAR(50),
                    exchange_acronym VARCHAR(20),
                    name VARCHAR(255),
                    currency VARCHAR(10),
                    market_cap DECIMAL(38, 18),
                    market_cap_usd DECIMAL(38, 18),
                    create_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
                    update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '修改时间'
                )
            """)
            
            if close_conn:
                conn.commit()
        except Exception as e:
            logger.error(f"Failed to create yahoo_stock table: {e}")
        finally:
            if close_conn and conn:
                conn.close()

    @staticmethod
    def upsert_yahoo_stock_batch(items: List[Dict[str, Any]]) -> int:
        if not items:
            return 0
        try:
            conn = DBManager.get_connection()
            cursor = conn.cursor()
            
            db_rows = []
            for item in items:
                db_rows.append((
                    item['yahoo_stock_symbol'],
                    item.get('yahoo_exchange_symbol', ''),
                    item.get('stock_symbol', ''),
                    item.get('exchange_acronym', ''),
                    item.get('name', ''),
                    item.get('currency', ''),
                    item.get('market_cap', 0),
                    item.get('market_cap_usd', 0)
                ))
            
            sql = """
                INSERT INTO fast_finance_yahoo_stock (
                    yahoo_stock_symbol, yahoo_exchange_symbol, stock_symbol, exchange_acronym, 
                    name, currency, market_cap, market_cap_usd
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    yahoo_exchange_symbol=VALUES(yahoo_exchange_symbol),
                    stock_symbol=VALUES(stock_symbol),
                    exchange_acronym=VALUES(exchange_acronym),
                    name=VALUES(name),
                    currency=VALUES(currency),
                    market_cap=VALUES(market_cap),
                    market_cap_usd=VALUES(market_cap_usd)
            """
            
            cursor.executemany(sql, db_rows)
            
            conn.commit()
            count = cursor.rowcount
            conn.close()
            return len(items)
        except Exception as e:
            logger.error(f"Error upserting yahoo stock batch: {e}")
            return 0

    @staticmethod
    def get_yahoo_stock_by_symbols(yahoo_symbols: List[str]) -> Dict[str, Dict[str, Any]]:
        if not yahoo_symbols:
            return {}
        try:
            import time
            start_ts = time.time()
            
            conn = DBManager.get_connection()
            cursor = conn.cursor()
            
            placeholders = ','.join(['%s'] * len(yahoo_symbols))
            sql = f"SELECT * FROM fast_finance_yahoo_stock WHERE yahoo_stock_symbol IN ({placeholders})"
            cursor.execute(sql, yahoo_symbols)
            rows = cursor.fetchall()
            conn.close()
            
            duration_ms = (time.time() - start_ts) * 1000
            # user-requested log style: [DEBU] [duration] [rows] SQL
            logger.info(f"[DEBU] [{duration_ms:.2f} ms] [rows:{len(rows)}] SQL: {sql} Params: {yahoo_symbols}")
            
            result = {}
            for row in rows:
                result[row['yahoo_stock_symbol']] = row
            return result
        except Exception as e:
            logger.error(f"Error getting yahoo stocks by symbols: {e}")
            return {}

    @staticmethod
    def init_yahoo_stock_related_cache_table(conn_or_cursor=None):
        close_conn = False
        conn = None
        if conn_or_cursor is None:
            conn = DBManager.get_connection()
            cursor = conn.cursor()
            close_conn = True
        else:
            if hasattr(conn_or_cursor, 'execute'):
                cursor = conn_or_cursor
            else:
                cursor = conn_or_cursor.cursor()

        try:
            # cursor.execute("DROP TABLE IF EXISTS fast_finance_yahoo_stock_related_cache")
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS fast_finance_yahoo_stock_related_cache (
                    id BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
                    symbol VARCHAR(50) UNIQUE NOT NULL,
                    data LONGTEXT,
                    create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
                    update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                )
            """)
            if close_conn:
                conn.commit()
        except Exception as e:
            logger.error(f"Failed to create yahoo_stock_related_cache table: {e}")
        finally:
            if close_conn and conn:
                conn.close()

    @staticmethod
    def get_yahoo_stock_related_cache(symbol: str) -> Optional[Dict[str, Any]]:
        try:
            conn = DBManager.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT data, create_time FROM fast_finance_yahoo_stock_related_cache WHERE symbol = %s", (symbol,))
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return {
                    "data": row["data"],
                    "created_at": row["create_time"] # App expects created_at
                }
            return None
        except Exception as e:
            logger.error(f"Error getting related cache for {symbol}: {e}")
            return None

    @staticmethod
    def upsert_yahoo_stock_related_cache(symbol: str, data: str):
        try:
            conn = DBManager.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO fast_finance_yahoo_stock_related_cache (symbol, data)
                VALUES (%s, %s)
                ON DUPLICATE KEY UPDATE data=VALUES(data)
            """, (symbol, data))
            
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"Error upserting related cache for {symbol}: {e}")
