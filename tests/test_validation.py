import os
import sys

# Ensure absolute path resolution for imports
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(os.path.join(ROOT_DIR, 'src'))

from database.database import create_connection

def validate_insertion():
    try:
        conn = create_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM projects;")
        projects_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM project_snapshots;")
        snapshots_count = cursor.fetchone()[0]
        
        print(f"Projects count: {projects_count}")
        print(f"Project snapshots count: {snapshots_count}")
        
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        print(f"Error validating tables: {e}")
        return False

if __name__ == "__main__":
    validate_insertion()
