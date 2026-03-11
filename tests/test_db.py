import os
import sys

# Ensure absolute path resolution for imports
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(os.path.join(ROOT_DIR, 'src'))

from database.database import create_connection

def test_connection():
    try:
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT current_database();")
        db_name = cursor.fetchone()[0]
        print(f"Successfully connected to PostgreSQL database: {db_name}")
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        print(f"Error connecting to the database: {e}")
        return False

if __name__ == "__main__":
    if test_connection():
        sys.exit(0)
    else:
        sys.exit(1)
