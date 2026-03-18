import os

content = """
## Phase 9 — Live Data Refresh Pipeline

### Architecture
The project now includes an end-to-end, on-demand data refresh pipeline to fetch new Kickstarter projects, append them to the existing dataset, and retrain the model.

1. **Scraping**: `src/scraper/crawler.py` and `src/scraper/parser.py` are executed via `scripts/scrape_kickstarter.py`. Due to Kickstarter's dynamic Cloudflare protections, the MVP scraper extracts `__NEXT_DATA__` JSON or raw HTML cards to pull live project information. The output is persisted to `data/raw/scraped_projects.csv`.
2. **Schema Normalization**: `scripts/update_dataset.py` reads historical Kaggle data and the newly scraped CSV, maps column names and ensures date formats are standard, drops duplicates, and exports a unified `data/processed/full_dataset.csv`.
3. **Model Retraining**: `scripts/retrain_model.py` calls the main `train.py` logic which reads from the `full_dataset.csv`. After training, the model is versioned into `models/model_YYYYMMDD.joblib` and `models/latest.joblib`.
4. **API Integration**: The API now reads categories map directly from `data/processed/full_dataset.csv` and loads inferences via `models/latest.joblib`.

### How to Run
Manually trigger the full pipeline in a single command using:
```bash
python scripts/refresh_pipeline.py
```
This script sequentially executes the scraper, the dataset updater, and the retraining script.
"""

with open('d:/Proyecto_Kickstarter/WALKTHROUGH.md', 'a', encoding='utf-8') as f:
    f.write(content)

print("Appended successfully")
