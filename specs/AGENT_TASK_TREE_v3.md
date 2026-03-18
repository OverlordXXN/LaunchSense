# AGENT_TASK_TREE_v3
Kickstarter Viability Analyzer

Total tasks: 47
Completed tasks: 43

------------------------------------------------
PHASE 1 — PROJECT SETUP [COMPLETED]
------------------------------------------------

[X] TASK-001 setup logging module
[X] TASK-002 implement config loader
[X] TASK-003 implement project path utilities
[X] TASK-004 setup environment variables
[X] TASK-005 implement PostgreSQL connection

------------------------------------------------
PHASE 2 — DATA PIPELINE (INGESTION & SCRAPER) [COMPLETED]
------------------------------------------------

[X] TASK-006 load Kaggle dataset
[X] TASK-007 inspect dataset schema
[X] TASK-008 normalize column names
[X] TASK-009 convert date columns
[X] TASK-010 compute project duration
[X] TASK-011 compute success label
[X] TASK-012 save cleaned dataset
[X] TASK-013 create database schema
[X] TASK-014 create projects and project_snapshots tables
[X] TASK-015 implement DB insertion utilities
[X] TASK-016 implement discover page crawler
[X] TASK-017 scrape live project pages and metadata
[X] TASK-018 unify Kaggle and scraped schemas
[X] TASK-019 normalize currencies
[X] TASK-020 compute analytics engine structural features (density, success rates)

------------------------------------------------
PHASE 3 — MODEL TRAINING PIPELINE [COMPLETED]
------------------------------------------------

[X] TASK-021 build training dataset generator
[X] TASK-022 train baseline Logistic Regression model
[X] TASK-023 evaluate LR accuracy and AUC
[X] TASK-024 train Random Forest ensemble model
[X] TASK-025 evaluate RF accuracy, AUC, and feature importance
[X] TASK-026 train XGBoost gradient boosting model
[X] TASK-027 evaluate XGB accuracy, AUC, and feature importance
[X] TASK-028 compare models and select best performer (XGBoost)
[X] TASK-029 serialize and save trained models via joblib
[X] TASK-030 document training phases in WALKTHROUGH.md

------------------------------------------------
PHASE 4 — PREDICTION / INFERENCE PIPELINE [COMPLETED]
------------------------------------------------

[X] TASK-031 build pre-launch prediction interface
[X] TASK-032 implement prediction engine utilizing the saved XGBoost model
[X] TASK-033 map raw project inputs to model feature space
[X] TASK-034 implement Goal Optimization Logic
[X] TASK-035 output probability of success and feature contribution breakdown

------------------------------------------------
PHASE 5 — API LAYER [COMPLETED]
------------------------------------------------

[X] TASK-036 setup FastAPI / Flask application
[X] TASK-037 implement `/predict` viability endpoint
[X] TASK-038 implement `/optimize` goal recommendation endpoint

------------------------------------------------
PHASE 6 — WEB DEMO [COMPLETED]
------------------------------------------------

[X] TASK-039 build frontend demo interface (HTML/JS/CSS or Streamlit)
[X] TASK-040 create form for user project parameters (goal, category, duration, etc.)
[X] TASK-041 display three types of insights: 1. Predicted probability of success (from the ML model), 2. Funding goal optimization, 3. Feature contribution breakdown

------------------------------------------------
PHASE 7 — UI ENHANCEMENTS [COMPLETED]
------------------------------------------------

[X] TASK-042 implement goal optimization curve visualization
[X] TASK-043 display probability vs goal interactive chart

------------------------------------------------
PHASE 8 — ADVANCED ANALYTICS & UX [COMPLETED]
------------------------------------------------

[X] TASK-044 implement SHAP waterfall-style explanation view
[X] TASK-045 add dynamic category/subcategory selector from dataset
[X] TASK-046 implement similar projects comparison panel
[X] TASK-047 enhance UI layout and visual hierarchy (Streamlit UX improvements)

--------------------------------------------------
PHASE 9 — LIVE DATA PIPELINE (SCRAPING + RETRAINING) [COMPLETED]
--------------------------------------------------

[X] TASK-053 implement discover page crawler (Kickstarter discover pages with pagination)
[X] TASK-054 implement project page parser (extract __NEXT_DATA__ JSON and required fields)

[X] TASK-055 implement scraper runner (crawl URLs + parse projects end-to-end)
[X] TASK-056 persist scraped data to CSV (data/raw/scraped_projects.csv)

[X] TASK-057 implement schema normalization (align scraped data with Kaggle dataset format)
[X] TASK-058 merge scraped data with historical dataset (data/processed/full_dataset.csv)

[X] TASK-059 implement retraining trigger script (reuse existing training pipeline)
[X] TASK-060 implement model versioning (models/model_YYYYMMDD.joblib + models/latest.joblib)

[X] TASK-061 update API data loading to use unified dataset (categories + similarity endpoints)
[X] TASK-062 update API model loading to always use latest model

[X] TASK-063 implement refresh_pipeline.py (scrape → process → retrain end-to-end)

--------------------------------------------------
PHASE 10 — LIVE DATA PIPELINE (HARDENING & RELIABILITY) [COMPLETED]
--------------------------------------------------

[X] TASK-064 implement duplicate control in dataset merge
[X] TASK-065 add logging to pipeline scripts (scraping, dataset update, retraining)
[X] TASK-066 implement basic error handling in refresh_pipeline
[X] TASK-067 limit scraping scope (pagination or max projects safeguard)
--------------------------------------------------
PATCH TASK — SCRAPER 403 FIX (HEADERS INJECTION) [COMPLETED]
--------------------------------------------------

[X] TASK-068 update HTTP requests in crawler to include headers
[X] TASK-069 ensure response validation
[X] TASK-070 optional: introduce requests.Session()
