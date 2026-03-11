import os
import sys
import logging

# Ensure absolute path resolution for imports
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(os.path.join(ROOT_DIR, 'src'))

from pipeline.loader import load_kaggle_dataset
from pipeline.normalization import unify_schemas
from database.database import create_connection, insert_projects, insert_project_snapshots

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    dataset_path = os.path.join(ROOT_DIR, 'data', 'raw', 'kaggle', 'kickstarter_projects.csv')
    
    if not os.path.exists(dataset_path):
        logger.error(f"Dataset not found at {dataset_path}")
        logger.info("Please ensure Phase 2 completed successfully and the Kaggle dataset is in the correct path.")
        return
        
    logger.info("Starting historical data ingestion pipeline...")
    
    # 1. Load the dataset
    logger.info(f"Loading dataset from {dataset_path}...")
    try:
        df = load_kaggle_dataset(dataset_path)
        logger.info(f"Loaded {len(df)} rows.")
    except Exception as e:
        logger.error(f"Failed to load dataset: {e}")
        return
    
    # 2. Normalize it
    logger.info("Normalizing the dataset schemas...")
    try:
        projects_df, project_snapshots_df = unify_schemas(df)
        logger.info(f"Generated projects_df with shape: {projects_df.shape}")
        logger.info(f"Generated project_snapshots_df with shape: {project_snapshots_df.shape}")
    except Exception as e:
        logger.error(f"Failed to normalize datasets: {e}")
        return
    
    # Connect to the database
    logger.info("Connecting to the PostgreSQL database...")
    try:
        conn = create_connection()
    except Exception as e:
        logger.error(f"Failed to connect to database. Ensure PostgreSQL is running. Error: {e}")
        return
        
    try:
        # Start transaction handled by execute_values committing at the end of the function call
        # but the connection handles the top-level block
        
        # 3. Insert projects into the database
        logger.info("Inserting projects...")
        insert_projects(projects_df, conn=conn)
        
        # 4. Insert project snapshots
        logger.info("Inserting project snapshots...")
        insert_project_snapshots(project_snapshots_df, conn=conn)
        
        conn.commit()
        logger.info("Phase 3 pipeline execution complete! Data ingestion was successful.")
    except Exception as e:
        conn.rollback()
        logger.error(f"Ingestion failed. Transaction rolled back: {e}")
    finally:
        conn.close()
        logger.info("Database connection closed.")

if __name__ == "__main__":
    main()
