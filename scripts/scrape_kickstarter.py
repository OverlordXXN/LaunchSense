import os
import sys
import pandas as pd

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.scraper.crawler import crawl_discover_page
from src.scraper.parser import extract_project_data

# TASK-067: Scraping Scope Limitation
MAX_PAGES = 5
MAX_PROJECTS = 100

def create_empty_csv():
    columns = ['project_id', 'name', 'category', 'subcategory', 'country', 'currency', 'goal', 'launched_at', 'deadline', 'pledged', 'backers', 'state', 'url']
    df = pd.DataFrame(columns=columns)
    out_dir = os.path.join('data', 'raw')
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, 'scraped_projects.csv')
    if not os.path.exists(out_path):
        df.to_csv(out_path, index=False)
        print("Created empty scraped_projects.csv")

def main():
    print("Starting Kickstarter manual scraping...")
    urls = crawl_discover_page(limit=MAX_PAGES)
    
    if not urls:
        print("No URLs found. Exiting.")
        create_empty_csv()
        return

    data = []
    # Scraping a limited number of projects for MVP testing to avoid excessive load
    for i, url in enumerate(urls[:MAX_PROJECTS]):
        print(f"Scraping [{i+1}/{min(len(urls), MAX_PROJECTS)}] {url}")
        project_data = extract_project_data(url)
        if project_data:
            data.append(project_data)
            
    if data:
        df = pd.DataFrame(data)
        out_dir = os.path.join('data', 'raw')
        os.makedirs(out_dir, exist_ok=True)
        out_path = os.path.join(out_dir, 'scraped_projects.csv')
        
        if os.path.exists(out_path):
            existing_df = pd.read_csv(out_path)
            full_df = pd.concat([existing_df, df]).drop_duplicates(subset=['project_id'], keep='last')
            full_df.to_csv(out_path, index=False)
            print(f"Appended {len(df)} records. Total scraped now: {len(full_df)}.")
        else:
            df.to_csv(out_path, index=False)
            print(f"Saved {len(df)} records to new CSV.")
    else:
        create_empty_csv()

if __name__ == '__main__':
    main()
