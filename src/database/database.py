import os
import logging
import pandas as pd
import psycopg2
import psycopg2.extras
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

def create_connection():
    """
    Establish a connection to the PostgreSQL database using environment variables or defaults.
    """
    # Load environment variables from .env file
    load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), '.env'))
    
    host = os.environ.get('DB_HOST', 'localhost')
    database = os.environ.get('DB_NAME', 'kickstarter')
    user = os.environ.get('DB_USER', 'postgres')
    password = os.environ.get('DB_PASSWORD', 'postgres')
    port = os.environ.get('DB_PORT', '5432')
    
    conn = psycopg2.connect(
        host=host,
        database=database,
        user=user,
        password=password,
        port=port
    )
    return conn

def insert_projects(projects_df: pd.DataFrame, conn=None):
    """
    Insert a normalization dataframe of projects into the 'projects' table.
    Uses execute_values for fast batch insertion.
    """
    if projects_df.empty:
        logger.info("projects_df is empty. Skipping insertion.")
        return

    close_conn_after = False
    if conn is None:
        conn = create_connection()
        close_conn_after = True

    columns = [
        'project_id', 'name', 'category', 'subcategory', 'country', 
        'currency', 'goal', 'created_at', 'launched_at', 'deadline'
    ]
    
    # Filter only available columns to match the DataFrame
    cols_to_insert = [col for col in columns if col in projects_df.columns]
    
    if 'project_id' not in cols_to_insert:
        raise ValueError("projects_df must contain 'project_id' column")

    # Handle NaNs
    df_clean = projects_df[cols_to_insert].where(pd.notnull(projects_df[cols_to_insert]), None)
    
    # Check if dates need to be converted to str or datetime timestamp
    # pandas where converts empty to None which psycopg2 gracefully handles
    # but values should be a list of tuples
    
    values = [tuple(x) for x in df_clean.to_numpy()]
    
    query = f"""
    INSERT INTO projects ({', '.join(cols_to_insert)})
    VALUES %s
    ON CONFLICT (project_id) DO NOTHING;
    """

    cursor = conn.cursor()
    try:
        psycopg2.extras.execute_values(
            cursor, query, values, page_size=10000
        )
        if close_conn_after:
            conn.commit()
        logger.info(f"Successfully inserted/updated {len(values)} projects.")
    except Exception as e:
        if close_conn_after:
            conn.rollback()
        logger.error(f"Error inserting projects: {e}")
        raise
    finally:
        cursor.close()
        if close_conn_after:
            conn.close()

def insert_project_snapshots(project_snapshots_df: pd.DataFrame, conn=None):
    """
    Insert a normalization dataframe of snapshots into the 'project_snapshots' table.
    Uses execute_values for fast batch insertion.
    """
    if project_snapshots_df.empty:
        logger.info("project_snapshots_df is empty. Skipping insertion.")
        return

    close_conn_after = False
    if conn is None:
        conn = create_connection()
        close_conn_after = True

    columns = ['project_id', 'snapshot_time', 'pledged', 'backers', 'state']
    cols_to_insert = [col for col in columns if col in project_snapshots_df.columns]
    
    if 'project_id' not in cols_to_insert:
        raise ValueError("project_snapshots_df must contain 'project_id' column")

    df_clean = project_snapshots_df[cols_to_insert].where(pd.notnull(project_snapshots_df[cols_to_insert]), None)
    values = [tuple(x) for x in df_clean.to_numpy()]
    
    query = f"""
    INSERT INTO project_snapshots ({', '.join(cols_to_insert)})
    VALUES %s;
    """

    cursor = conn.cursor()
    try:
        psycopg2.extras.execute_values(
            cursor, query, values, page_size=10000
        )
        if close_conn_after:
            conn.commit()
        logger.info(f"Successfully inserted {len(values)} project snapshots.")
    except Exception as e:
        if close_conn_after:
            conn.rollback()
        logger.error(f"Error inserting project snapshots: {e}")
        raise
    finally:
        cursor.close()
        if close_conn_after:
            conn.close()
