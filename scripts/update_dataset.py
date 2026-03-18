import os
import pandas as pd

def main():
    print("Starting Dataset Merge & Normalization...")
    kaggle_path = os.path.join('data', 'raw', 'kaggle', 'kickstarter_projects.csv')
    scraped_path = os.path.join('data', 'raw', 'scraped_projects.csv')
    out_path = os.path.join('data', 'processed', 'full_dataset.csv')
    
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    
    if not os.path.exists(kaggle_path):
        print(f"Error: Kaggle dataset not found at {kaggle_path}. Cannot proceed.")
        return
        
    df_kaggle = pd.read_csv(kaggle_path)
    print(f"Loaded {len(df_kaggle)} Kaggle projects.")
    
    if os.path.exists(scraped_path):
        df_scraped = pd.read_csv(scraped_path)
        
        if not df_scraped.empty:
            print(f"Loaded {len(df_scraped)} scraped projects for merge.")
            # Map scraped columns to Kaggle columns
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
            
            # Format state from lower case to capitalized as in Kaggle data ("Successful", "Failed")
            if 'State' in df_scraped.columns:
                df_scraped['State'] = df_scraped['State'].astype(str).str.capitalize()
                
            # Align columns
            common_cols = [c for c in df_kaggle.columns if c in df_scraped.columns]
            df_scraped = df_scraped[common_cols]
            
            # Ensure proper typing
            df_scraped['ID'] = pd.to_numeric(df_scraped['ID'], errors='coerce')
            df_scraped = df_scraped.dropna(subset=['ID'])
            df_scraped['ID'] = df_scraped['ID'].astype('int64')

            print("Merging datasets...")
            # Handle duplicated IDs by dropping from kaggle first
            scraped_ids = df_scraped['ID'].unique()
            df_kaggle = df_kaggle[~df_kaggle['ID'].isin(scraped_ids)]
            
            # Concatenate
            df_full = pd.concat([df_kaggle, df_scraped], ignore_index=True)
            
            # Phase 10: Task 064 - Duplicate control
            df_full = df_full.drop_duplicates(subset=["Name", "Launched"], keep="last")
        else:
            print("Scraped data CSV is empty. Using only kaggle data.")
            df_full = df_kaggle.copy()
    else:
        print("No scraped_projects.csv found. Using only kaggle data.")
        df_full = df_kaggle.copy()
        
    df_full.to_csv(out_path, index=False)
    print(f"Successfully generated full_dataset.csv with {len(df_full)} rows.")

if __name__ == '__main__':
    main()
