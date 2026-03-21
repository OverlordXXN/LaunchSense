import os
import pandas as pd

def parse_unix_dates(df, columns):
    for col in columns:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], unit='s', errors='coerce').dt.tz_localize(None).astype(str)
    return df

def main():
    print("Starting Dataset Merge & Normalization...")
    kaggle_path = os.path.join('data', 'raw', 'kaggle', 'kickstarter_projects.csv')
    kaggle_2025_path = os.path.join('data', 'raw', 'kaggle', 'kickstarter_may_2025.csv')
    scraped_path = os.path.join('data', 'raw', 'scraped_projects.csv')
    out_path = os.path.join('data', 'processed', 'full_dataset.csv')
    
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    
    dfs_to_concat = []
    
    # 1. Load Kaggle 2018
    if not os.path.exists(kaggle_path):
        print(f"Error: Kaggle dataset not found at {kaggle_path}. Cannot proceed.")
        return
    df_kaggle = pd.read_csv(kaggle_path)
    df_kaggle['data_source'] = "kaggle_2018"
    print(f"Loaded {len(df_kaggle)} Kaggle 2018 projects.")
    dfs_to_concat.append(df_kaggle)
    
    # Target columns
    target_cols = ['ID', 'Name', 'Category', 'Subcategory', 'Country', 'Launched', 'Deadline', 'Goal', 'Pledged', 'Backers', 'State', 'data_source']
    
    # 2. Load Kaggle 2025
    if os.path.exists(kaggle_2025_path):
        # Read low_memory=False to avoid DtypeWarning
        df_2025 = pd.read_csv(kaggle_2025_path, low_memory=False)
        print(f"Loaded {len(df_2025)} Kaggle 2025 projects.")
        
        map_2025 = {
            'id': 'ID',
            'name': 'Name',
            'category_parent_name': 'Category',
            'category_name': 'Subcategory',
            'country': 'Country',
            'launched_at': 'Launched',
            'deadline': 'Deadline',
            'goal': 'Goal',
            'pledged': 'Pledged',
            'backers_count': 'Backers',
            'state': 'State'
        }
        df_2025 = df_2025.rename(columns=map_2025)
        df_2025['data_source'] = "kaggle_2025"
        
        # Parse Unix dates
        df_2025 = parse_unix_dates(df_2025, ['Launched', 'Deadline'])
        
        if 'State' in df_2025.columns:
            df_2025['State'] = df_2025['State'].astype(str).str.capitalize()
            
        common_cols_2025 = [c for c in target_cols if c in df_2025.columns]
        df_2025 = df_2025[common_cols_2025]
        dfs_to_concat.append(df_2025)
    
    # 3. Load Scraped
    if os.path.exists(scraped_path):
        df_scraped = pd.read_csv(scraped_path)
        if not df_scraped.empty:
            print(f"Loaded {len(df_scraped)} scraped projects for merge.")
            scrape_map = {
                'project_id': 'ID',
                'name': 'Name',
                'category': 'Category',
                'subcategory': 'Subcategory',
                'country': 'Country',
                'launched_at': 'Launched',
                'deadline': 'Deadline',
                'goal': 'Goal',
                'pledged': 'Pledged',
                'backers': 'Backers',
                'state': 'State'
            }
            df_scraped = df_scraped.rename(columns=scrape_map)
            df_scraped['data_source'] = "scraped_live"
            
            if 'State' in df_scraped.columns:
                df_scraped['State'] = df_scraped['State'].astype(str).str.capitalize()
                
            common_cols_scraped = [c for c in target_cols if c in df_scraped.columns]
            df_scraped = df_scraped[common_cols_scraped]
            
            # Ensure proper typing for ID
            df_scraped['ID'] = pd.to_numeric(df_scraped['ID'], errors='coerce')
            df_scraped = df_scraped.dropna(subset=['ID'])
            df_scraped['ID'] = df_scraped['ID'].astype('int64')
            
            dfs_to_concat.append(df_scraped)
        else:
            print("No live data available — using Kaggle datasets only.")
    else:
        print("No live data available — using Kaggle datasets only.")

    print("\nMerging datasets...")
    df_full = pd.concat(dfs_to_concat, ignore_index=True)
    
    rows_before = len(df_full)
    
    # Prepare Launched for deduplication and year extraction
    df_full['Launched'] = pd.to_datetime(df_full['Launched'], errors='coerce')
    
    # Duplicate control
    df_full = df_full.drop_duplicates(subset=["Name", "Launched"], keep="last")
    
    rows_after = len(df_full)
    duplicates_removed = rows_before - rows_after
    
    # Phase 11 - Add launch_year
    df_full['launch_year'] = df_full['Launched'].dt.year
    
    # Logging
    print(f"rows before merge: {rows_before}")
    print(f"rows after merge: {rows_after}")
    print(f"number of duplicates removed: {duplicates_removed}")
    print("distribution of data_source:")
    print(df_full['data_source'].value_counts().to_string())
    
    df_full.to_csv(out_path, index=False)
    print(f"\nSuccessfully generated full_dataset.csv with {len(df_full)} rows.")

if __name__ == '__main__':
    main()
