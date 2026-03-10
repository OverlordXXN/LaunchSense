import pandas as pd
from datetime import datetime

COUNTRY_CURRENCY_MAP = {
    'US': 'USD', 'GB': 'GBP', 'CA': 'CAD', 'AU': 'AUD', 
    'EU': 'EUR', 'CH': 'CHF', 'DK': 'DKK', 'NO': 'NOK', 
    'SE': 'SEK', 'N,0"': 'USD', 'MX': 'MXN', 'NZ': 'NZD',
    'SG': 'SGD', 'IE': 'EUR', 'HK': 'HKD', 'IT': 'EUR',
    'DE': 'EUR', 'NL': 'EUR', 'FR': 'EUR', 'ES': 'EUR',
    'BE': 'EUR', 'AT': 'EUR', 'JP': 'JPY', 'LU': 'EUR'
}

def normalize_currencies(df: pd.DataFrame) -> pd.DataFrame:
    """
    Normalizes pledges to a common currency or infers currency from country.
    """
    # For Kaggle dataset, infer currency from country.
    if 'currency' not in df.columns and 'Country' in df.columns:
        df['currency'] = df['Country'].map(COUNTRY_CURRENCY_MAP).fillna('USD')
    return df

def standardize_dates(df: pd.DataFrame) -> pd.DataFrame:
    # Convert 'Launched' and 'Deadline' to datetime
    if 'Launched' in df.columns:
        df['launched_at'] = pd.to_datetime(df['Launched'], errors='coerce')
    if 'Deadline' in df.columns:
        df['deadline'] = pd.to_datetime(df['Deadline'], errors='coerce')
    
    # Kaggle dataset does not have created_at, default to launched_at
    if 'created_at' not in df.columns and 'launched_at' in df.columns:
        df['created_at'] = df['launched_at']
        
    return df

def unify_schemas(historical_df: pd.DataFrame, scraped_df: pd.DataFrame = None) -> tuple:
    """
    Combine datasets with a unified schema before inserting into DB.
    Returns (projects_df, project_snapshots_df) matching DATA_SCHEMA.
    """
    df = historical_df.copy()
    
    # 1. Base standardizations
    df = normalize_currencies(df)
    df = standardize_dates(df)
    
    # 2. Schema mapping
    column_mapping = {
        'ID': 'project_id',
        'Name': 'name',
        'Category': 'category',
        'Subcategory': 'subcategory',
        'Country': 'country',
        'Goal': 'goal',
        'Pledged': 'pledged',
        'Backers': 'backers',
        'State': 'state'
    }
    df = df.rename(columns=column_mapping)
    
    # Ensure project_id is string
    if 'project_id' in df.columns:
        df['project_id'] = df['project_id'].astype(str)
        
    # Handle missing values
    if 'goal' in df.columns:
        df['goal'] = df['goal'].fillna(0.0)
    if 'pledged' in df.columns:
        df['pledged'] = df['pledged'].fillna(0.0)
    if 'backers' in df.columns:
        df['backers'] = df['backers'].fillna(0).astype(int)
    if 'name' in df.columns:
        df['name'] = df['name'].fillna('Unknown')
        
    # Snapshot time
    df['snapshot_time'] = datetime.utcnow()
    
    # 3. Split into the two target tables
    project_cols = ['project_id', 'name', 'category', 'subcategory', 'country', 
                    'currency', 'goal', 'created_at', 'launched_at', 'deadline']
    snapshot_cols = ['project_id', 'snapshot_time', 'pledged', 'backers', 'state']
    
    # Filter columns that exist in the dataframe
    avail_project_cols = [c for c in project_cols if c in df.columns]
    avail_snapshot_cols = [c for c in snapshot_cols if c in df.columns]
    
    projects_df = df[avail_project_cols].drop_duplicates(subset=['project_id'])
    project_snapshots_df = df[avail_snapshot_cols]
    
    return projects_df, project_snapshots_df

