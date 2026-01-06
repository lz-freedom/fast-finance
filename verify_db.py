import sys
import os

# Ensure we can import app modules
sys.path.append(os.getcwd())

from app.core.database import DBManager
from app.core.config import settings

def test_connection():
    try:
        print(f"Testing connection to {settings.MYSQL_SERVER}...")
        conn = DBManager.get_connection()
        print("Connection successful!")
        
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
        print(f"Ping result: {result}")
        conn.close()
        
        print("Initializing tables...")
        DBManager.init_db()
        print("Tables initialized.")
        return True
    except Exception as e:
        print(f"Connection failed: {e}")
        return False

if __name__ == "__main__":
    if test_connection():
        sys.exit(0)
    else:
        sys.exit(1)
