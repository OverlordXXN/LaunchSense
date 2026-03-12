import os
import sys
import logging
import pandas as pd
import numpy as np


from database.database import create_connection

logger = logging.getLogger(__name__)

def fetch_historical_raw_data() -> pd.DataFrame:
    """
    Fetches the combined historical dataset from the local PostgreSQL database.
    """
    logger.info("Connecting to database to fetch historical projects...")
    conn = create_connection()
    query = """
    SELECT 
        p.project_id, p.name, p.category, p.subcategory, 
        p.country, p.currency, p.goal, p.launched_at, p.deadline,
        s.pledged, s.backers, s.state
    FROM projects p
    JOIN project_snapshots s ON p.project_id = s.project_id;
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

def _compute_competition_density(df: pd.DataFrame) -> pd.DataFrame:
    """
    Counts the number of other projects launched in the same category
    within a ±30 day rolling window from launched_at using numpy searchsorted.
    """
    logger.info("Computing competition density (+/- 30 days)...")
    
    # Sort dataframe by launched_at
    idx_orig = df['project_id'].copy()
    df = df.sort_values('launched_at').reset_index(drop=True)
    
    # Needs to be purely numeric offsets for numpy
    time_arr = df['launched_at'].astype('int64').values
    thirty_days_ns = pd.Timedelta(days=30).value
    
    lower_bound = time_arr - thirty_days_ns
    upper_bound = time_arr + thirty_days_ns
    
    # Initialize empty competition density
    density_values = np.zeros(len(df), dtype=int)
    
    categories = df['category'].unique()
    
    # Process per category using fast numpy searchsorted
    for cat in categories:
        cat_mask = (df['category'] == cat).values
        cat_times = time_arr[cat_mask]
        
        # Elements for this category
        cat_lower_bounds = lower_bound[cat_mask]
        cat_upper_bounds = upper_bound[cat_mask]
        
        # Use searchsorted to find the bounds indices
        start_indices = np.searchsorted(cat_times, cat_lower_bounds, side='left')
        end_indices = np.searchsorted(cat_times, cat_upper_bounds, side='right')
        
        # Calculate density (-1 to exclude the project itself)
        density = (end_indices - start_indices) - 1
        
        # Ensure it never goes below 0 
        density_values[cat_mask] = np.maximum(density, 0)
        
    df['competition_density'] = density_values
    
    # Restore original index
    df.index = df['project_id']
    df = df.reindex(idx_orig).reset_index(drop=True)
    
    return df

def build_analytics_features() -> pd.DataFrame:
    """
    Computes analytical features from the historical Postgres dataset.
    Returns a dataframe ready for ML model training.
    """
    df = fetch_historical_raw_data()
    
    if df.empty:
        logger.warning("Historical dataset is empty.")
        return df
        
    logger.info(f"Loaded {len(df)} projects. Computing features...")
    
    # 0. Set up date boundaries correctly
    df['launched_at'] = pd.to_datetime(df['launched_at'])
    df['deadline'] = pd.to_datetime(df['deadline'])
    df['duration_days'] = (df['deadline'] - df['launched_at']).dt.days

    # Extract temporal features
    df['launch_month'] = df['launched_at'].dt.month
    df['launch_day_of_week'] = df['launched_at'].dt.dayofweek
    df['campaign_duration'] = df['duration_days']


    # Base target metric: is_successful (1/0)
    df['is_successful'] = (df['state'].str.lower() == 'successful').astype(int)
    
    # 1. category_success_rate
    # 2. subcategory_success_rate
    logger.info("Computing category & subcategory success rates...")
    cat_success = df.groupby('category')['is_successful'].mean().rename('category_success_rate')
    df = df.merge(cat_success, on='category', how='left')
    
    subcat_success = df.groupby('subcategory')['is_successful'].mean().rename('subcategory_success_rate')
    df = df.merge(subcat_success, on='subcategory', how='left')
    
    # 3. goal_realism_score (Percentile of goal within category distribution)
    logger.info("Computing goal realism score...")
    # Fill nan goals with 0 before calculating percentiles
    df['goal'] = df['goal'].fillna(0)
    df['goal_realism_score'] = df.groupby('category')['goal'].rank(pct=True)
    
    # 4. competition_density
    df = _compute_competition_density(df)
    
    # 5. average_pledge_per_backer
    logger.info("Computing average pledge per backer...")
    df['average_pledge_per_backer'] = np.where(df['backers'] > 0, df['pledged'] / df['backers'], 0)
    
    logger.info("Feature engineering complete.")
    
    # Keep important base columns and the 5 new features
    # Return features and the target variable (is_successful)
    return df
