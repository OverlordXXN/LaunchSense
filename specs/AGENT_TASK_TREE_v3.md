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
[X] TASK-071 — GRACEFUL SCRAPER FAILURE HANDLING

--------------------------------------------------
PHASE 11 — DATASET UPDATE (MULTI-SOURCE MERGE) [COMPLETED]
--------------------------------------------------

[X] TASK-072 update_dataset.py logic to handle kaggle_may_2025 dataset
[X] TASK-073 extract launch_year and maintain data_source fields

--------------------------------------------------
PHASE 11 PATCH — ROBUST DATETIME PARSING [COMPLETED]
--------------------------------------------------

[X] TASK-074 handle heterogeneous dates avoiding crashes inside analytics engine

--------------------------------------------------
PHASE 12 — TEMPORAL MODEL ENHANCEMENT (DRIFT-AWARE) [COMPLETED]
--------------------------------------------------

[X] TASK-075 Train Baseline vs Enhanced tracking concept drift over launch_year
[X] TASK-076 Analyze SHAP global metrics testing modern data (>= 2020)

--------------------------------------------------
PHASE 13 — PRODUCTION MODEL STRATEGY (DRIFT-OPTIMIZED) [COMPLETED]
--------------------------------------------------

[X] TASK-077 Implement data filtering inside pre-launch XGBoost trainer natively (>= 2020)
[X] TASK-078 Hook scripts/retrain_model.py to trigger drift-model updates into models/latest.joblib and models/model_recent.joblib
[X] TASK-079 Embed modern assumptions warning strictly into src/prediction/predictor.py

--------------------------------------------------
PHASE 14 — MODEL VALIDATION & TRUST LAYER [COMPLETED]
--------------------------------------------------

[X] TASK-080 Configure API structure passing `confidence_level` arrays alongside out-of-bounds `warning_flags` natively
[X] TASK-081 Inject sklearn `calibration_curve` diagnostics inside XGBClassifier evaluation loops
[X] TASK-082 Modify `streamlit_app.py` natively surfacing dynamic warning bounds immediately above prediction rendering

--------------------------------------------------
PHASE 15 — UX POLISH & HUMAN-FRIENDLY INPUTS [COMPLETED]
--------------------------------------------------

[X] TASK-083 Map model month ranges onto `Jan-Dec` dictionaries seamlessly within the Streamlit payload array
[X] TASK-084 Translate daily numeric keys into standard `Mon-Sun` frontend displays preserving model mapping hooks
[X] TASK-085 Deploy temporal tracking disclaimers explicitly inside UI presentation parameters identifying `2020+` boundaries

--------------------------------------------------
BUGFIX PATCH — CATEGORY ENDPOINT FAULT TOLERANCE [COMPLETED]
--------------------------------------------------

[X] TASK-086 Refactor `/categories` decoupling mappings from ML dataset builders natively tracking `full_dataset.csv` directly
[X] TASK-087 Implement column normalization masking `category` and `subcategory` anomalies explicitly preventing query crashes
[X] TASK-088 Wrap dynamic dataset slices mapping safely inside `try/except` responding `{"Category": ["Sub"]}` identically masking 500 runtime faults

--------------------------------------------------
IMPROVEMENT PATCH — CATEGORY ENDPOINT TRANSPARENCY [COMPLETED]
--------------------------------------------------

[X] TASK-086 Refactor `/categories` decoupling mappings from ML dataset builders natively tracking `full_dataset.csv` directly
[X] TASK-087 Implement column normalization masking `category` and `subcategory` anomalies explicitly preventing query crashes
[X] TASK-088 Wrap dynamic dataset slices mapping safely inside `try/except` responding `{"Category": ["Sub"]}` identically masking 500 runtime faults

--------------------------------------------------
IMPROVEMENT PATCH — CATEGORY ENDPOINT TRANSPARENCY [COMPLETED]
--------------------------------------------------

[X] TASK-089 Refactor `/categories` payload mapping explicitly identifying `{"source": "dataset", "mapping": {...}}` natively.
[X] TASK-090 Modify Streamlit integrations securely rendering `st.warning()` dynamic boundaries explicitly when `source == "fallback"`.

--------------------------------------------------
PHASE 16 — TEXT NORMALIZATION & UX POLISH (CATEGORY LABELS) [COMPLETED]
--------------------------------------------------

[X] TASK-091 Improve category text normalization bypassing raw `.title()` logic 
[X] TASK-092 Fix apostrophe casing issues applying `re.sub(r"'S\b", "'s", ...)` bindings actively 
[X] TASK-093 Handle acronym formatting preserving `DIY`, `Sci-Fi`, and `3D` natively

--------------------------------------------------
PHASE 17 — UX ENHANCEMENTS (AUTOCOMPLETE & COMPARISON) [COMPLETED]
--------------------------------------------------

[X] TASK-094 Implement category UI Autocompletes rendering native `index=None` validating API payload defaults implicitly
[X] TASK-095 Architect Scenario Chart abstractions querying multiple prediction payload variants across distinct goals natively using Streamlit `st.bar_chart()`

--------------------------------------------------
PHASE 18 — FINAL UX POLISH [COMPLETED]
--------------------------------------------------

[X] TASK-096 Refine Streamlit interactive scenario arrays mapping explicit 5-point distributions `(-50%, -25%, Base, +25%, +50%)` natively plotting success decay probabilities across dynamic `st.line_chart` graphics natively.

--------------------------------------------------
PHASE 19 — API PERFORMANCE & RESILIENCE (CATEGORIES ENDPOINT) [COMPLETED]
--------------------------------------------------

[X] TASK-097 Cache category mappings migrating heavy payloads instantly intercepting at API startup  
[X] TASK-098 Prevent per-request heavy Pandas dataframe extraction scanning via `/categories`  
[X] TASK-099 Add API fallback safety structures neutralizing `500` dataset load failures natively 
[X] TASK-100 Increase Streamlit connectivity layers executing `timeout=20` mapping offline retry loops 
[X] TASK-101 Enforce frontend UI resilience validating `@st.cache_data` structures reliably

--------------------------------------------------
PHASE 20 — CONTEXTUAL INSIGHT ALIGNMENT [COMPLETED]
--------------------------------------------------

[X] TASK-102 Resolve conflicting messaging mapping ML optimization recommendations natively against Historical Context insights 
[X] TASK-103 Implement conditional 3-scenario evaluations comparing `rec_goal` precisely evaluating (+/- 10%) boundaries without contradictions

--------------------------------------------------
PHASE 21 — CLOUD DEPLOYMENT COMPATIBILITY [COMPLETED]
--------------------------------------------------

[X] TASK-104 detect cloud/standalone mode automatically
[X] TASK-105 load prediction model directly in Streamlit fallback
[X] TASK-106 dataset-based categories fallback (no API dependency)
[X] TASK-107 standalone goal optimization fallback
[X] TASK-108 add UI indicator for Standalone Cloud Mode

--------------------------------------------------
PHASE 22 — STANDALONE INFERENCE FIX [COMPLETED]
--------------------------------------------------

[X] TASK-109 enable standalone prediction execution
[X] TASK-110 remove API-only blocking message
[X] TASK-111 enable standalone optimization logic
[X] TASK-112 unify API and standalone prediction pipeline

--------------------------------------------------
PHASE 23 — BRANDING & PRODUCTION POLISH [COMPLETED]
--------------------------------------------------

[X] TASK-113 rename app title to LaunchSense
[X] TASK-114 add subtitle explaining product purpose
[X] TASK-115 add legal disclaimer (not affiliated with Kickstarter)
[X] TASK-116 add GitHub repo link in UI
[X] TASK-117 add Cloud Mode indicator styling
[X] TASK-118 add footer with version and dataset attribution
[X] TASK-119 add data source attribution (Kickstarter safe wording)

--------------------------------------------------
PHASE 25 — DATASET DECOUPLING [COMPLETED]
--------------------------------------------------

[X] TASK-124 remove CSV dependency from API startup
[X] TASK-125 implement static category mapping in backend
[X] TASK-126 ensure prediction works using only trained model
[X] TASK-127 gracefully disable historical analytics if dataset missing

--------------------------------------------------
PHASE 26 — STREAMLIT CLOUD API CONNECTION [COMPLETED]
--------------------------------------------------

[X] TASK-128 replace localhost API references
[X] TASK-129 introduce configurable API_BASE
[X] TASK-130 update all request calls to use API_BASE
[X] TASK-131 ensure fallback remains functional
[X] TASK-132 update UI mode detection logic

--------------------------------------------------
PHASE 27 — IMPORT PATH STABILIZATION [COMPLETED]
--------------------------------------------------

[X] TASK-133 add project root to PYTHONPATH
[X] TASK-134 fix standalone model imports
[X] TASK-135 fix API imports
[X] TASK-136 enforce API-first prediction flow

--------------------------------------------------
PHASE 28 — PRODUCTION MODEL + CATEGORY RESTORATION [COMPLETED]
--------------------------------------------------

[X] TASK-137 fix model absolute path
[X] TASK-138 lazy load model in API
[X] TASK-139 fix standalone model loading
[X] TASK-140 full category mapping for standalone
[X] TASK-141 unify categories API + standalone
[X] TASK-142 enforce API-first prediction

--------------------------------------------------
PHASE 29 — FIX RELATIVE IMPORTS FOR FASTAPI CONTAINER [COMPLETED]
--------------------------------------------------

[X] TASK-143 replace absolute api imports with relative
[X] TASK-144 convert internal api imports to relative
[X] TASK-145 ensure src/api/__init__.py exists
[X] TASK-146 remove sys.path hacks from Phase 27
[X] TASK-147 verify uvicorn src.api.app:app compatibility
