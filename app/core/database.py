import sqlite3
import os
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger("fastapi")


# Ensure data directory exists
DB_DIR = os.path.join(os.getcwd(), "data", "db")
if not os.path.exists(DB_DIR):
    os.makedirs(DB_DIR, exist_ok=True)

DB_PATH = os.path.join(DB_DIR, "stocks.db")

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
            
            conn.commit()
            conn.close()
            logger.info(f"Database initialized at {DB_PATH}")
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")

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
