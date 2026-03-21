import subprocess
import sys
import os

def main():
    print("=== Starting Kickstarter Data Refresh Pipeline ===")
    
    python_exec = sys.executable
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    
    steps = [
        ("1. Scraper", ["scripts/scrape_kickstarter.py"]),
        ("2. Dataset Merge/Normalization", ["scripts/update_dataset.py"]),
        ("3. Model Retraining", ["scripts/retrain_model.py"])
    ]
    
    for name, script_args in steps:
        print(f"\n--- Running {name} ---")
        try:
            # Join the script path explicitly
            script_path = os.path.join(base_dir, script_args[0])
            result = subprocess.run([python_exec, script_path], check=True, cwd=base_dir)
            print(f"{name} completed successfully.")
        except Exception as e:
            print(f"Pipeline failed at {name}. Error: {e}")
            print("Aborting pipeline to prevent data corruption.")
            sys.exit(1)
            
    print("\n--- DATA SOURCE SUMMARY ---")
    scraped_path = os.path.join(base_dir, 'data', 'raw', 'scraped_projects.csv')
    live_success = False
    if os.path.exists(scraped_path):
        try:
            with open(scraped_path, 'r', encoding='utf-8') as f:
                # Count lines. If > 1 (header + data), success.
                lines = sum(1 for _ in f)
                if lines > 1:
                    live_success = True
        except Exception:
            pass
            
    print(f"Live Scraping: {'SUCCESS' if live_success else 'FAILED'}")
    print("Kaggle Dataset: USED")
    
    dataset_path = os.path.join(base_dir, 'data', 'processed', 'full_dataset.csv')
    size = 0
    if os.path.exists(dataset_path):
        try:
            with open(dataset_path, 'r', encoding='utf-8') as f:
                size = sum(1 for _ in f) - 1 # exclude header
        except Exception:
            pass
    print(f"Final Dataset Size: {max(0, size)} rows")
    
    print("\n=== Pipeline Completed Successfully ===")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\nPipeline execution cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\nUnexpected pipeline failure: {e}")
        sys.exit(1)
