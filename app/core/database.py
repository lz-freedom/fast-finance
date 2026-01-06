import sqlite3
import os
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger("fastapi")


# Ensure data directory exists
DB_DIR = os.path.join(os.getcwd(), "data", "db")
if not os.path.exists(DB_DIR):
    try:
        os.makedirs(DB_DIR, exist_ok=True)
        # Verify permissions or just log success
        logger.info(f"Created database directory: {os.path.abspath(DB_DIR)}")
    except Exception as e:
        logger.error(f"Failed to create database directory {DB_DIR}: {e}")

DB_PATH = os.path.join(DB_DIR, "stocks.db")
logger.info(f"Using Database Path: {os.path.abspath(DB_PATH)}")

class SQLiteManager:
    @staticmethod
    def init_db():
        """
        Initialize the database and create tables if they don't exist.
        """
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            
            # Create stocks table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS stocks (
                    symbol TEXT PRIMARY KEY,
                    exchange_acronym TEXT,
                    name TEXT,
                    created_at TIMESTAMP,
                    updated_at TIMESTAMP
                )
            """)
            
            # Create tradingview_stock table
            SQLiteManager.init_tradingview_table(cursor)
            
            # Create investing_stock table
            SQLiteManager.init_investing_table(cursor)
            
            # Create stock_history_cache table
            SQLiteManager.init_history_cache_table(cursor)

            # Create yahoo_analysis_cache table
            SQLiteManager.init_analysis_cache_table(cursor)
            
            # Create yahoo_stock table
            SQLiteManager.init_yahoo_stock_table(cursor)

            # Create yahoo_stock_related_cache table
            SQLiteManager.init_yahoo_stock_related_cache_table(cursor)

            # Create job_execution_logs table
            SQLiteManager.init_job_log_table(cursor)
            
            conn.commit()
            conn.close()
            logger.info(f"Database initialized at {DB_PATH}")
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")

    # ... (existing methods)

    # --- Job Logging Methods ---

    @staticmethod
    def init_job_log_table(conn_or_cursor=None):
        """
        Create job_execution_logs table.
        """
        close_conn = False
        if conn_or_cursor is None:
            conn = sqlite3.connect(DB_PATH)
            # Enable column name access
            conn.row_factory = sqlite3.Row 
            cursor = conn.cursor()
            close_conn = True
        else:
            if hasattr(conn_or_cursor, 'execute'):
                cursor = conn_or_cursor
            else:
                cursor = conn_or_cursor.cursor()

        try:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS job_execution_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    job_id TEXT,
                    job_name TEXT,
                    status TEXT, -- 'RUNNING', 'SUCCESS', 'FAILED'
                    start_time TIMESTAMP,
                    end_time TIMESTAMP,
                    duration_seconds REAL,
                    message TEXT,
                    created_at TIMESTAMP
                )
            """)
            if close_conn:
                conn.commit()
        except Exception as e:
            logger.error(f"Failed to create job_execution_logs table: {e}")
        finally:
            if close_conn:
                conn.close()

    @staticmethod
    def log_job_start(job_id: str, job_name: str) -> int:
        """
        Log job start. Returns inserted row ID.
        """
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            now = datetime.now()
            
            cursor.execute("""
                INSERT INTO job_execution_logs (job_id, job_name, status, start_time, created_at)
                VALUES (?, ?, 'RUNNING', ?, ?)
            """, (job_id, job_name, now, now))
            
            row_id = cursor.lastrowid
            conn.commit()
            conn.close()
            return row_id
        except Exception as e:
            logger.error(f"Error logging job start: {e}")
            return -1

    @staticmethod
    def log_job_finish(log_id: int, status: str, message: str = ""):
        """
        Log job finish (SUCCESS or FAILED).
        """
        if log_id < 0:
            return
            
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            now = datetime.now()
            
            # Fetch start time to calculate duration
            cursor.execute("SELECT start_time FROM job_execution_logs WHERE id = ?", (log_id,))
            row = cursor.fetchone()
            start_time = None
            if row:
                if isinstance(row[0], str): # if stored as ISO string by sqlite adapter
                    try:
                        start_time = datetime.fromisoformat(row[0])
                    except:
                        pass
                else:
                    start_time = row[0]
            
            duration = 0.0
            if start_time:
                duration = (now - start_time).total_seconds()
            
            cursor.execute("""
                UPDATE job_execution_logs 
                SET status = ?, end_time = ?, duration_seconds = ?, message = ?
                WHERE id = ?
            """, (status, now, duration, message, log_id))
            
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"Error logging job finish: {e}")

    @staticmethod
    def get_job_logs(limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get latest job logs.
        """
        try:
            conn = sqlite3.connect(DB_PATH)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM job_execution_logs ORDER BY id DESC LIMIT ?", (limit,))
            rows = cursor.fetchall()
            conn.close()
            return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Error getting job logs: {e}")
            return []


    @staticmethod
    def upsert_stock(symbol: str, exchange_acronym: str, name: str) -> bool:
        """
        Insert a new stock or update existing one.
        Returns True if it was a NEW insertion, False if updated/ignored.
        """
        is_new = False
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            
            # Check if exists
            cursor.execute("SELECT symbol FROM stocks WHERE symbol = ?", (symbol,))
            exists = cursor.fetchone()
            
            now = datetime.now()
            
            if not exists:
                cursor.execute("""
                    INSERT INTO stocks (symbol, exchange_acronym, name, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?)
                """, (symbol, exchange_acronym, name, now, now))
                is_new = True
            else:
                cursor.execute("""
                    UPDATE stocks 
                    SET exchange_acronym = ?, name = ?, updated_at = ?
                    WHERE symbol = ?
                """, (exchange_acronym, name, now, symbol))
                
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"Error upserting stock {symbol}: {e}")
            
        return is_new

    @staticmethod
    def upsert_stocks_batch(stocks: List[Dict[str, str]]) -> Dict[str, int]:
        """
        Batch upsert stocks.
        Returns {"new": count, "processed": count}
        stocks list item expected keys: 'symbol', 'exchange_acronym', 'name'
        """
        stats = {"new": 0, "processed": 0}
        if not stocks:
            return stats

        try:
            conn = sqlite3.connect(DB_PATH)
            # Optimize: Use WAL mode? Or just standard transaction
            cursor = conn.cursor()
            
            now = datetime.now()
            
            # Prepare data
            # To distinguish new vs update, checking one by one is slow?
            # Or use INSERT OR IGNORE then update?
            # SQLite upsert syntax: INSERT INTO ... ON CONFLICT(symbol) DO UPDATE ...
            # Available in recent sqlite versions.
            
            # Let's try standard ON CONFLICT logic (SQLite 3.24+)
            # But to count "new", it's tricky with bulk upsert.
            
            # For simplicity/robustness without complex counting logic:
            # We can select all existing symbols first.
            symbols = [s['symbol'] for s in stocks]
            placeholders = ','.join(['?'] * len(symbols))
            cursor.execute(f"SELECT symbol FROM stocks WHERE symbol IN ({placeholders})", symbols)
            existing = set(row[0] for row in cursor.fetchall())
            
            new_rows = []
            update_rows = []
            
            for s in stocks:
                sym = s['symbol']
                if sym in existing:
                    update_rows.append((s['exchange_acronym'], s['name'], now, sym))
                else:
                    new_rows.append((sym, s['exchange_acronym'], s['name'], now, now))
                    stats["new"] += 1
                stats["processed"] += 1
            
            if new_rows:
                cursor.executemany("""
                    INSERT INTO stocks (symbol, exchange_acronym, name, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?)
                """, new_rows)
            
            if update_rows:
                cursor.executemany("""
                    UPDATE stocks 
                    SET exchange_acronym = ?, name = ?, updated_at = ?
                    WHERE symbol = ?
                """, update_rows)
                
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error in batch upsert: {e}")
            # Fallback or re-raise? Logging is enough, batch fails.
            
        return stats

    @staticmethod
    def get_stocks_after(start_time: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """
        Get stocks created after the specified time.
        """
        try:
            conn = sqlite3.connect(DB_PATH)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            if start_time:
                cursor.execute("SELECT * FROM stocks WHERE created_at >= ?", (start_time,))
            else:
                cursor.execute("SELECT * FROM stocks")
                
            rows = cursor.fetchall()
            conn.close()
            
            return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Error getting stocks: {e}")
            return []

    # --- TradingView Sync Methods ---

    @staticmethod
    def init_tradingview_table(conn_or_cursor=None):
        """
        Create tradingview_stock table.
        """
        # If conn is passed, use it, else create new
        close_conn = False
        if conn_or_cursor is None:
            conn = sqlite3.connect(DB_PATH)
            # Enable column name access for migration checks
            conn.row_factory = sqlite3.Row 
            cursor = conn.cursor()
            close_conn = True
        else:
            # If it's a cursor, use it. If conn, get cursor.
            if hasattr(conn_or_cursor, 'execute'):
                cursor = conn_or_cursor
            else:
                cursor = conn_or_cursor.cursor()

        try:
            # 1. Create table with ALL columns if not exists
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tradingview_stock (
                    tradingview_full_stock_symbol TEXT PRIMARY KEY,
                    stock_symbol TEXT,
                    exchange_acronym TEXT,
                    name TEXT,
                    description TEXT,
                    logoid TEXT,
                    logo_url TEXT,
                    
                    ipo_offer_date TEXT,
                    ipo_offer_price REAL,
                    ipo_deal_amount REAL,
                    sector_tr TEXT,
                    sector TEXT,
                    
                    created_at TIMESTAMP,
                    updated_at TIMESTAMP
                )
            """)
            
            # 2. Lazy Migration: Check if new columns exist, if not add them
            # This handles the case where table exists but new columns don't
            try:
                # Get existing columns
                cursor.execute("PRAGMA table_info(tradingview_stock)")
                columns = [row[1] for row in cursor.fetchall()]
                
                new_cols = {
                    "ipo_offer_date": "TEXT",
                    "ipo_offer_price": "REAL",
                    "ipo_deal_amount": "REAL",
                    "sector_tr": "TEXT",
                    "sector": "TEXT"
                }
                
                for col_name, col_type in new_cols.items():
                    if col_name not in columns:
                        logger.info(f"Migrating tradingview_stock: adding {col_name} column")
                        cursor.execute(f"ALTER TABLE tradingview_stock ADD COLUMN {col_name} {col_type}")
                        
            except Exception as e:
                logger.error(f"Migration check failed: {e}")

            if close_conn:
                conn.commit()
        except Exception as e:
            logger.error(f"Failed to create tradingview_stock table: {e}")
        finally:
            if close_conn:
                conn.close()

    @staticmethod
    def init_investing_table(conn_or_cursor=None):
        """
        Create investing_stock table.
        """
        # If conn is passed, use it, else create new
        close_conn = False
        if conn_or_cursor is None:
            conn = sqlite3.connect(DB_PATH)
            # Enable column name access for migration checks
            conn.row_factory = sqlite3.Row 
            cursor = conn.cursor()
            close_conn = True
        else:
            if hasattr(conn_or_cursor, 'execute'):
                cursor = conn_or_cursor
            else:
                cursor = conn_or_cursor.cursor()

        try:
            # 1. Create table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS investing_stock (
                    investing_stock_pair_id INTEGER PRIMARY KEY,
                    investing_stock_uid TEXT,
                    tradingview_full_stock_symbol TEXT,
                    stock_symbol TEXT,
                    exchange_acronym TEXT,
                    logo_url TEXT,
                    
                    name_cn TEXT,
                    name_en TEXT,
                    investing_sector_cn TEXT,
                    investing_sector_en TEXT,
                    investing_industry_cn TEXT,
                    investing_industry_en TEXT,
                    
                    created_at TIMESTAMP,
                    updated_at TIMESTAMP
                )
            """)
            
            # 2. Lazy Migration check (optional for new table but good practice)
            
            if close_conn:
                conn.commit()
        except Exception as e:
            logger.error(f"Failed to create investing_stock table: {e}")
        finally:
            if close_conn:
                conn.close()

    @staticmethod
    def upsert_tradingview_batch(items: List[Dict[str, Any]]) -> int:
        """
        Batch upsert tradingview stocks.
        Returns number of processed items.
        """
        if not items:
            return 0
            
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            # Fix timezone: Docker is UTC, User wants Beijing Time (UTC+8)
            # simplest way without extra deps is utcnow + 8h
            from datetime import timedelta
            now = datetime.utcnow() + timedelta(hours=8)
            
            db_rows = []
            for item in items:
                # Construct URL if logoid present
                logoid = item.get('logoid', '')
                logo_url = f"https://s3-symbol-logo.tradingview.com/{logoid}.svg" if logoid else ""
                
                db_rows.append((
                   item['tradingview_full_stock_symbol'],
                   item.get('stock_symbol', ''),
                   item.get('exchange_acronym', ''),
                   item.get('name', ''),
                   item.get('description', ''),
                   logoid,
                   logo_url,
                   
                   item.get('ipo_offer_date'),
                   item.get('ipo_offer_price'),
                   item.get('ipo_deal_amount'),
                   item.get('sector_tr'),
                   item.get('sector'),
                   
                   now, # created_at (ignored on update)
                   now  # updated_at
                ))

            # Upsert syntax (requires SQLite 3.24+)
            cursor.executemany("""
                INSERT INTO tradingview_stock (
                    tradingview_full_stock_symbol, stock_symbol, exchange_acronym, name, 
                    description, logoid, logo_url, 
                    ipo_offer_date, ipo_offer_price, ipo_deal_amount, sector_tr, sector,
                    created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(tradingview_full_stock_symbol) DO UPDATE SET
                    stock_symbol=excluded.stock_symbol,
                    exchange_acronym=excluded.exchange_acronym,
                    name=excluded.name,
                    description=excluded.description,
                    logoid=excluded.logoid,
                    logo_url=excluded.logo_url,
                    ipo_offer_date=excluded.ipo_offer_date,
                    ipo_offer_price=excluded.ipo_offer_price,
                    ipo_deal_amount=excluded.ipo_deal_amount,
                    sector_tr=excluded.sector_tr,
                    sector=excluded.sector,
                    updated_at=excluded.updated_at
            """, db_rows)
            
            conn.commit()
            count = cursor.rowcount
            conn.close()
            return len(items) # rowcount might be diff with upsert (can be 0 if no change or >1)
        except Exception as e:
            logger.error(f"Error upserting tradingview batch: {e}")
            return 0

    @staticmethod
    def get_tradingview_stocks(exchange_acronym: Optional[str] = None, 
                               min_created_at: Optional[datetime] = None) -> List[Dict[str, Any]]:
        try:
            conn = sqlite3.connect(DB_PATH)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            query = "SELECT * FROM tradingview_stock WHERE 1=1"
            params = []
            
            if exchange_acronym:
                query += " AND exchange_acronym = ?"
                params.append(exchange_acronym)
            
            if min_created_at:
                query += " AND created_at >= ?"
                params.append(min_created_at)
                
            cursor.execute(query, tuple(params))
            rows = cursor.fetchall()
            conn.close()
            return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Error fetching tradingview stocks: {e}")
            return []

    @staticmethod
    def cleanup_tradingview_duplicates() -> int:
        """
        Delete symbols ending with .U if a corresponding .UN or .UM symbol exists.
        Returns number of deleted rows.
        """
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            
            # Subquery to find duplicates
            # Rule: Delete X.U if X.UN exists
            # Rule: Delete X.U if X.UM exists
            
            # Using basic SQL for compatibility
            # DELETE FROM tradingview_stock WHERE tradingview_full_stock_symbol LIKE '%.U' AND 
            # (
            #   EXISTS (SELECT 1 FROM tradingview_stock t2 WHERE t2.tradingview_full_stock_symbol = SUBSTR(tradingview_stock.tradingview_full_stock_symbol, 1, LENGTH(tradingview_stock.tradingview_full_stock_symbol)-2) || '.UN')
            #   OR
            #   EXISTS (SELECT 1 FROM tradingview_stock t3 WHERE t3.tradingview_full_stock_symbol = SUBSTR(tradingview_stock.tradingview_full_stock_symbol, 1, LENGTH(tradingview_stock.tradingview_full_stock_symbol)-2) || '.UM')
            # )
            
            # Simpler with REPLACE if we assume standard format
            # REPLACE(sym, '.U', '.UN') works if .U is at end.
            
            sql = """
            DELETE FROM tradingview_stock 
            WHERE tradingview_full_stock_symbol LIKE '%.U' 
            AND (
                EXISTS (
                    SELECT 1 FROM tradingview_stock t2 
                    WHERE t2.tradingview_full_stock_symbol = REPLACE(tradingview_stock.tradingview_full_stock_symbol, '.U', '.UN')
                )
                OR
                EXISTS (
                    SELECT 1 FROM tradingview_stock t3 
                    WHERE t3.tradingview_full_stock_symbol = REPLACE(tradingview_stock.tradingview_full_stock_symbol, '.U', '.UM')
                )
            )
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
        """
        Batch upsert investing stocks.
        Returns number of processed items.
        """
        if not items:
            return 0
            
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            
            # Fix timezone: Docker is UTC, User wants Beijing Time (UTC+8)
            from datetime import timedelta
            now = datetime.utcnow() + timedelta(hours=8)
            
            db_rows = []
            for item in items:
                db_rows.append((
                   item['investing_stock_pair_id'],
                   item.get('investing_stock_uid', ''),
                   item.get('tradingview_full_stock_symbol', ''),
                   item.get('stock_symbol', ''),
                   item.get('exchange_acronym', ''),
                   item.get('logo_url', ''),
                   
                   item.get('name_cn'),
                   item.get('name_en'),
                   item.get('investing_sector_cn'),
                   item.get('investing_sector_en'),
                   item.get('investing_industry_cn'),
                   item.get('investing_industry_en'),
                   
                   now, # created_at 
                   now  # updated_at
                ))

            # Upsert
            cursor.executemany("""
                INSERT INTO investing_stock (
                    investing_stock_pair_id, investing_stock_uid, tradingview_full_stock_symbol,
                    stock_symbol, exchange_acronym, logo_url,
                    name_cn, name_en, 
                    investing_sector_cn, investing_sector_en,
                    investing_industry_cn, investing_industry_en,
                    created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(investing_stock_pair_id) DO UPDATE SET
                    investing_stock_uid=excluded.investing_stock_uid,
                    tradingview_full_stock_symbol=excluded.tradingview_full_stock_symbol,
                    stock_symbol=excluded.stock_symbol,
                    exchange_acronym=excluded.exchange_acronym,
                    logo_url=excluded.logo_url,
                    
                    -- Only update names/sector/industry if new value is not null?
                    -- Or just overwrite. Overwriting is safer for sync.
                    -- But we have dual updates (CN fetch updates CN fields, EN fetch updates EN fields).
                    -- If we do full overwrite, we might wipe the other language if we pass None.
                    -- Solution: In service, we merge beforehand OR we use COALESCE in SQL.
                    -- Let's use COALESCE(excluded.col, table.col) to keep existing if new is null.
                    
                    name_cn=COALESCE(excluded.name_cn, investing_stock.name_cn),
                    name_en=COALESCE(excluded.name_en, investing_stock.name_en),
                    investing_sector_cn=COALESCE(excluded.investing_sector_cn, investing_stock.investing_sector_cn),
                    investing_sector_en=COALESCE(excluded.investing_sector_en, investing_stock.investing_sector_en),
                    investing_industry_cn=COALESCE(excluded.investing_industry_cn, investing_stock.investing_industry_cn),
                    investing_industry_en=COALESCE(excluded.investing_industry_en, investing_stock.investing_industry_en),
                    
                    updated_at=excluded.updated_at
            """, db_rows)
            
            conn.commit()
            count = cursor.rowcount
            conn.close()
            return len(items)
        except Exception as e:
            logger.error(f"Error upserting investing batch: {e}")
            return 0

    @staticmethod
    def get_investing_stocks(exchange_acronym: Optional[str] = None, min_created_at: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """
        Get investing stocks with optional filters.
        """
        try:
            conn = sqlite3.connect(DB_PATH)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            query = "SELECT * FROM investing_stock WHERE 1=1"
            params = []
            
            if exchange_acronym:
                query += " AND exchange_acronym = ?"
                params.append(exchange_acronym)
                
            if min_created_at:
                query += " AND created_at >= ?"
                params.append(min_created_at)
                
            cursor.execute(query, tuple(params))
            rows = cursor.fetchall()
            conn.close()
            return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Error fetching investing stocks: {e}")
            return []

    # --- History Cache Methods ---

    @staticmethod
    def init_history_cache_table(conn_or_cursor=None):
        """
        Create stock_history_cache table.
        """
        close_conn = False
        if conn_or_cursor is None:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            close_conn = True
        else:
            if hasattr(conn_or_cursor, 'execute'):
                cursor = conn_or_cursor
            else:
                cursor = conn_or_cursor.cursor()

        try:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS stock_history_cache (
                    cache_key TEXT PRIMARY KEY,
                    data TEXT,
                    created_at TIMESTAMP
                )
            """)
            if close_conn:
                conn.commit()
        except Exception as e:
            logger.error(f"Failed to create stock_history_cache table: {e}")
        finally:
            if close_conn:
                conn.close()

    @staticmethod
    def get_history_cache(cache_key: str) -> Optional[str]:
        """
        Get cached history data (JSON string).
        Returns None if not found.
        """
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("SELECT data FROM stock_history_cache WHERE cache_key = ?", (cache_key,))
            row = cursor.fetchone()
            conn.close()
            return row[0] if row else None
        except Exception as e:
            logger.error(f"Error getting history cache: {e}")
            return None

    @staticmethod
    def upsert_history_cache(cache_key: str, data: str):
        """
        Upsert history cache data.
        """
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            now = datetime.now()
            
            # Using REPLACE INTO for simplicity as key is PK
            cursor.execute("""
                REPLACE INTO stock_history_cache (cache_key, data, created_at)
                VALUES (?, ?, ?)
            """, (cache_key, data, now))
            
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"Error upserting history cache: {e}")

    # --- Analysis Cache Methods ---

    @staticmethod
    def init_analysis_cache_table(conn_or_cursor=None):
        """
        Create yahoo_analysis_cache table.
        """
        close_conn = False
        if conn_or_cursor is None:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            close_conn = True
        else:
            if hasattr(conn_or_cursor, 'execute'):
                cursor = conn_or_cursor
            else:
                cursor = conn_or_cursor.cursor()

        try:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS yahoo_analysis_cache (
                    symbol TEXT PRIMARY KEY,
                    data TEXT,
                    created_at TIMESTAMP
                )
            """)
            if close_conn:
                conn.commit()
        except Exception as e:
            logger.error(f"Failed to create yahoo_analysis_cache table: {e}")
        finally:
            if close_conn:
                conn.close()

    @staticmethod
    def get_analysis_cache(symbol: str) -> Optional[Dict[str, Any]]:
        """
        Get cached analysis data.
        Returns dict with keys: data (json strings), created_at (datetime)
        """
        try:
            conn = sqlite3.connect(DB_PATH, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT data, created_at FROM yahoo_analysis_cache WHERE symbol = ?", (symbol,))
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return {
                    "data": row["data"],
                    "created_at": row["created_at"]
                }
            return None
        except Exception as e:
            logger.error(f"Error getting analysis cache for {symbol}: {e}")
            return None

    @staticmethod
    def upsert_analysis_cache(symbol: str, data: str):
        """
        Upsert analysis cache data.
        """
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            now = datetime.now()
            
            cursor.execute("""
                REPLACE INTO yahoo_analysis_cache (symbol, data, created_at)
                VALUES (?, ?, ?)
            """, (symbol, data, now))
            
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"Error upserting analysis cache for {symbol}: {e}")
    @staticmethod
    def init_yahoo_stock_table(conn_or_cursor=None):
        """
        Create yahoo_stock table.
        """
        close_conn = False
        if conn_or_cursor is None:
            conn = sqlite3.connect(DB_PATH)
            # Enable column name access for migration checks
            conn.row_factory = sqlite3.Row 
            cursor = conn.cursor()
            close_conn = True
        else:
            if hasattr(conn_or_cursor, 'execute'):
                cursor = conn_or_cursor
            else:
                cursor = conn_or_cursor.cursor()

        try:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS yahoo_stock (
                    yahoo_stock_symbol TEXT PRIMARY KEY,
                    yahoo_exchange_symbol TEXT,
                    stock_symbol TEXT,
                    exchange_acronym TEXT,
                    name TEXT,
                    currency TEXT,
                    market_cap TEXT,
                    market_cap_usd TEXT,
                    created_at TIMESTAMP,
                    updated_at TIMESTAMP
                )
            """)
            
            # Lazy Migration for new columns
            try:
                cursor.execute("PRAGMA table_info(yahoo_stock)")
                columns = [row[1] for row in cursor.fetchall()]
                
                new_cols = {
                    "currency": "TEXT",
                    "market_cap": "TEXT",
                    "market_cap_usd": "TEXT"
                }
                
                for col_name, col_type in new_cols.items():
                    if col_name not in columns:
                        logger.info(f"Migrating yahoo_stock: adding {col_name} column")
                        cursor.execute(f"ALTER TABLE yahoo_stock ADD COLUMN {col_name} {col_type}")
                        
            except Exception as e:
                logger.error(f"Migration check failed: {e}")
            if close_conn:
                conn.commit()
        except Exception as e:
            logger.error(f"Failed to create yahoo_stock table: {e}")
        finally:
            if close_conn:
                conn.close()

    @staticmethod
    def upsert_yahoo_stock_batch(items: List[Dict[str, Any]]) -> int:
        """
        Batch upsert yahoo stocks.
        """
        if not items:
            return 0
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            now = datetime.now()
            
            db_rows = []
            for item in items:
                db_rows.append((
                    item['yahoo_stock_symbol'],
                    item.get('yahoo_exchange_symbol', ''),
                    item.get('stock_symbol', ''),
                    item.get('exchange_acronym', ''),
                    item.get('name', ''),
                    item.get('currency', ''),
                    str(item.get('market_cap', '0')),
                    str(item.get('market_cap_usd', '0')),
                    now, # created_at
                    now  # updated_at
                ))
            
            cursor.executemany("""
                INSERT INTO yahoo_stock (
                    yahoo_stock_symbol, yahoo_exchange_symbol, stock_symbol, exchange_acronym, 
                    name, currency, market_cap, market_cap_usd, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(yahoo_stock_symbol) DO UPDATE SET
                    yahoo_exchange_symbol=excluded.yahoo_exchange_symbol,
                    stock_symbol=excluded.stock_symbol,
                    exchange_acronym=excluded.exchange_acronym,
                    name=excluded.name,
                    currency=excluded.currency,
                    market_cap=excluded.market_cap,
                    market_cap_usd=excluded.market_cap_usd,
                    updated_at=excluded.updated_at
            """, db_rows)
            
            conn.commit()
            count = cursor.rowcount
            conn.close()
            return len(items)
        except Exception as e:
            logger.error(f"Error upserting yahoo stock batch: {e}")
            return 0

    @staticmethod
    def get_yahoo_stock_by_symbols(yahoo_symbols: List[str]) -> Dict[str, Dict[str, Any]]:
        """
        Get yahoo stocks by a list of yahoo symbols.
        Returns a dict mapping {yahoo_symbol: {data}}
        """
        if not yahoo_symbols:
            return {}
        try:
            import time
            start_ts = time.time()
            
            conn = sqlite3.connect(DB_PATH)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            placeholders = ','.join(['?'] * len(yahoo_symbols))
            sql = f"SELECT * FROM yahoo_stock WHERE yahoo_stock_symbol IN ({placeholders})"
            cursor.execute(sql, yahoo_symbols)
            rows = cursor.fetchall()
            conn.close()
            
            duration_ms = (time.time() - start_ts) * 1000
            # user-requested log style: [DEBU] [duration] [rows] SQL
            logger.info(f"[DEBU] [{duration_ms:.2f} ms] [rows:{len(rows)}] SQL: {sql} Params: {yahoo_symbols}")
            
            result = {}
            for row in rows:
                r = dict(row)
                result[r['yahoo_stock_symbol']] = r
            return result
        except Exception as e:
            logger.error(f"Error getting yahoo stocks by symbols: {e}")
            return {}

    @staticmethod
    def init_yahoo_stock_related_cache_table(conn_or_cursor=None):
        """
        Create yahoo_stock_related_cache table.
        """
        close_conn = False
        if conn_or_cursor is None:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            close_conn = True
        else:
            if hasattr(conn_or_cursor, 'execute'):
                cursor = conn_or_cursor
            else:
                cursor = conn_or_cursor.cursor()

        try:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS yahoo_stock_related_cache (
                    symbol TEXT PRIMARY KEY,
                    data TEXT,
                    created_at TIMESTAMP
                )
            """)
            if close_conn:
                conn.commit()
        except Exception as e:
            logger.error(f"Failed to create yahoo_stock_related_cache table: {e}")
        finally:
            if close_conn:
                conn.close()

    @staticmethod
    def get_yahoo_stock_related_cache(symbol: str) -> Optional[Dict[str, Any]]:
        """
        Get cached related stock data.
        """
        try:
            conn = sqlite3.connect(DB_PATH, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT data, created_at FROM yahoo_stock_related_cache WHERE symbol = ?", (symbol,))
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return {
                    "data": row["data"],
                    "created_at": row["created_at"]
                }
            return None
        except Exception as e:
            logger.error(f"Error getting related cache for {symbol}: {e}")
            return None

    @staticmethod
    def upsert_yahoo_stock_related_cache(symbol: str, data: str):
        """
        Upsert related stock cache.
        """
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            now = datetime.now()
            
            cursor.execute("""
                REPLACE INTO yahoo_stock_related_cache (symbol, data, created_at)
                VALUES (?, ?, ?)
            """, (symbol, data, now))
            
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"Error upserting related cache for {symbol}: {e}")

    # End of Class
