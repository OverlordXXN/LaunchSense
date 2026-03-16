# Kickstarter Project Scaffolding Walkthrough

Based on the [Project Spec](file:///d:/Proyecto_Kickstarter/specs/kickstarter_PROJECT_SPEC.txt) and the detailed subsystem specifications, the initial structure of the Kickstarter Viability Analyzer has been successfully created.

## Executed Module Scaffolding

The following Python packages and interfaces have been implemented:

### 1. `src/scraper/`
Responsible for manual discovery and data extraction of live Kickstarter projects.
- [scraper/__init__.py](file:///d:/Proyecto_Kickstarter/src/scraper/__init__.py)
- [scraper/run_scraper.py](file:///d:/Proyecto_Kickstarter/src/scraper/run_scraper.py) - Primary execution entry point `python src/scraper/run_scraper.py`.
- [scraper/crawler.py](file:///d:/Proyecto_Kickstarter/src/scraper/crawler.py) - Handles the `discover` page pagination navigation.
- [scraper/parser.py](file:///d:/Proyecto_Kickstarter/src/scraper/parser.py) - Extracts metadata embedded in the `__NEXT_DATA__` JSON chunk.

### 2. `src/pipeline/`
Responsible for data ingestion, normalization, and PostgreSQL database ingestion.
- [pipeline/loader.py](file:///d:/Proyecto_Kickstarter/src/pipeline/loader.py) - Historical Kaggle dataset loader.
- [pipeline/database.py](file:///d:/Proyecto_Kickstarter/src/pipeline/database.py) - Interfaces for DB connections and inserting project snapshots.
- [pipeline/normalization.py](file:///d:/Proyecto_Kickstarter/src/pipeline/normalization.py) - Logic to standardize currencies and unify Kaggle with live scraped data.

### 3. `src/analytics/`
The core statistics, velocity matching engine from [ANALYTICS_ENGINE_SPEC.md](file:///d:/Proyecto_Kickstarter/specs/ANALYTICS_ENGINE_SPEC.md).
- [analytics/similarity.py](file:///d:/Proyecto_Kickstarter/src/analytics/similarity.py) - `find_similar_projects(...)` logic.
- [analytics/statistics.py](file:///d:/Proyecto_Kickstarter/src/analytics/statistics.py) - `compute_medians(...)` and `compute_average_pledge(...)`.
- [analytics/funding_analysis.py](file:///d:/Proyecto_Kickstarter/src/analytics/funding_analysis.py) - Functions to assess funding velocity and estimation tools.
- [analytics/analytics_service.py](file:///d:/Proyecto_Kickstarter/src/analytics/analytics_service.py) - The main export interface `analyze_project(...)`.

### 4. `src/models/`
Machine learning models for viability.
- [models/predict.py](file:///d:/Proyecto_Kickstarter/src/models/predict.py) - Interface to load models and estimate `predict_success_probability(...)`.
- [models/train.py](file:///d:/Proyecto_Kickstarter/src/models/train.py) - Pipeline for training the initial Logistic Regression models.

## Validation Results

- **Syntax Validation:** Ran `python -m compileall src/` which passed with zero errors. All scaffolding files contain syntactically valid python definitions.
- **Specification Match:** The folder structure exactly matches the described logic required by the user specifications.

The scaffolding completes Phase 1's architecture understanding and structure preparation, allowing the engineering team / agents to now focus on the implementations of individual components (e.g. historical data ingestion or scraper implementation) safely within clean designated modules.

---

# Phase 2: Historical Data Ingestion Pipeline Execution

The system is now capable of loading the historical Kaggle dataset and preparing it for PostgreSQL insertion by strictly mapping the schema.

## Implemented Modules

### Loader (`src/pipeline/loader.py`)
- Reads `data/raw/kaggle/kickstarter_projects.csv` securely into a Pandas DataFrame.

### Normalizer (`src/pipeline/normalization.py`)
- Standardizes inconsistent date formats (`Launched`, `Deadline` -> `launched_at`, `deadline`).
- Uses `Country` to map the `currency` assuming local currency (e.g., 'US' -> 'USD', 'GB' -> 'GBP') via `COUNTRY_CURRENCY_MAP`.
- Separates the flattened `historical_df` into two exact `DATA_SCHEMA.sql` matching tables: `projects` and `project_snapshots`.
- Cleans and default-pads values (`goal=0.0`, `backers=0`).

## Validation Results

- Successfully ran `test_pipeline.py`.
- Evaluated `374,853` rows.
- Generated `projects_df` columns: `['project_id', 'name', 'category', 'subcategory', 'country', 'currency', 'goal', 'created_at', 'launched_at', 'deadline']`.
- Generated `project_snapshots_df` columns: `['project_id', 'snapshot_time', 'pledged', 'backers', 'state']`.

The dataframe structures are perfectly synced with the requested schema.

## CHECKPOINT

Phase 2 completed successfully.

Dataset:
374,853 Kickstarter projects loaded and normalized.

Next step planned:
Phase 3 - PostgreSQL persistence layer.

Modules to implement next:
- src/database/database.py
- scripts/ingest_historical_data.py

---

# Phase 3: Repository Restructure and Import Stabilization

After the initial scaffolding and historical ingestion pipeline validation, the repository underwent a structural stabilization phase to ensure reliable module resolution and agent-safe execution.

The objective of this phase was to align the project with a **standard Python src-layout architecture** and eliminate import instability across scripts, modules, and tests.

## Repository Structure

The project now follows the recommended Python project layout:

Proyecto_Kickstarter/
│
├── src/
│   ├── analytics/
│   ├── database/
│   ├── models/
│   ├── pipeline/
│   └── scraper/
│
├── tests/
├── scripts/
├── data/
├── config/
├── specs/
└── WALKTHROUGH.md

All application code now lives inside the `src/` directory, which acts as the package root.

## Import Path Stabilization

Several inconsistencies caused by earlier development iterations were corrected.

### Corrections Applied

1. **Tests Import Strategy**

All test modules now dynamically append the `src` directory to the Python path:

```
sys.path.append(os.path.join(ROOT_DIR, "src"))
```

This guarantees that modules such as:

```
from analytics.analytics_engine import build_analytics_features
```

resolve correctly during test execution.

2. **Removal of Internal Path Manipulation**

Modules inside `src/` previously contained temporary `sys.path` manipulation used during early debugging stages.

These have been completely removed to ensure that:

* Modules remain pure and import-safe.
* Entry points (tests or scripts) control the runtime environment.

3. **Package Initialization Fix**

A missing package initializer was added:

```
src/database/__init__.py
```

This ensures the `database` module behaves as a valid Python package.

## Validation Results

The stabilization phase was validated by executing the test suite.

Successful executions include:

* `tests/test_analytics.py`
* `tests/test_validation.py`
* `tests/test_db.py`

All previous `ModuleNotFoundError` issues have been resolved.

The repository is now considered **import-stable**.

---

# Current Development Status

At this point the project has completed:

• Core module scaffolding
• Historical dataset ingestion pipeline
• Repository structure stabilization
• Test suite validation

The system is now ready to move into the **machine learning stage**.

---

# Next Development Phase

The next engineering milestone is the implementation of the **model training pipeline**.

Target module:

```
src/models/train.py
```

The objective is to train the first predictive model estimating the probability that a Kickstarter project will successfully fund.

Planned pipeline flow:

```
PostgreSQL Historical Dataset
        ↓
Analytics Feature Engineering
        ↓
Training Dataset Generation
        ↓
Model Training (Logistic Regression baseline)
        ↓
Prediction Interface
```

---

# Agent Continuation Note

Future development agents should continue work starting from the **model training stage**, focusing on implementing the logic inside:

```
src/models/train.py
```

The analytics feature layer and data ingestion pipeline are already prepared to support the training workflow.

---

## Phase 4 – Baseline Model Training

The goal of this phase was to construct an initial predictive machine learning model to estimate the probability that a Kickstarter project will fund successfully.

**Features Used:**
- `goal`
- `goal_realism_score`
- `category_success_rate`
- `subcategory_success_rate`
- `competition_density`
- `average_pledge_per_backer`

**Model Selected:**
- Baseline Scikit-Learn `LogisticRegression(max_iter=1000)`

**Dataset Configuration:**
- Total Dataset Size: 374,853
- Training Set: 299,882 (80%)
- Testing Set: 74,971 (20%)

**Evaluation Metrics (Test Set):**
- **Accuracy:** 0.7201
- **ROC AUC:** 0.7854

**Model Artifact Output:**
- The trained prediction model is successfully saved at: `src/models/kickstarter_success_model.pkl`

---

## Phase 5 – Random Forest Model

**Objective:**
To train a more robust ensemble model in order to improve upon the prediction performance established by the baseline Logistic Regression model.

**Model Chosen:**
- `RandomForestClassifier(n_estimators=200, max_depth=None, random_state=42, n_jobs=-1)`

**Evaluation Metrics (Test Set):**
- **Accuracy:** 0.7617
- **ROC AUC:** 0.8501

**Comparison with Logistic Regression (Phase 4):**
- **Accuracy Improvement:** +0.0416 (from 0.7201 to 0.7617)
- **ROC AUC Improvement:** +0.0647 (from 0.7854 to 0.8501)
The Random Forest classifier showed a considerable boost in ROC AUC, suggesting it is significantly better at distinguishing successful and failed projects than the linear base model.

**Feature Importances:**
1. `average_pledge_per_backer`: 60.09% 
2. `goal`: 14.32%
3. `goal_realism_score`: 12.54%
4. `subcategory_success_rate`: 9.55%
5. `category_success_rate`: 2.22%
6. `competition_density`: 1.27%

The `average_pledge_per_backer` emerged as the most dominant predictive feature. Structural goals (`goal` and `goal_realism_score`) also showed strong predictive signals. 

**Model Artifact Output:**
- The trained random forest model is successfully saved at: `src/models/kickstarter_random_forest_model.pkl`

---

## Phase 6 – Gradient Boosting Model (XGBoost)

**Objective:**
To train an XGBoost classifier and compare its predictive capability with the Logistic Regression and Random Forest models. The ensemble boosting method aims to iteratively correct errors and squeeze more signal out of the features.

**Model Chosen:**
- `XGBClassifier(n_estimators=300, max_depth=6, learning_rate=0.05, subsample=0.8, colsample_bytree=0.8, random_state=42, n_jobs=-1)`

**Evaluation Metrics (Test Set):**
- **Accuracy:** 0.8009
- **ROC AUC:** 0.8837

**Comparison with Previous Models:**
- **vs Logistic Regression (Phase 4):** Accuracy +0.0808 | ROC AUC +0.0983
- **vs Random Forest (Phase 5):** Accuracy +0.0392 | ROC AUC +0.0336
XGBoost is the top-performing model so far, offering a robust ~80% accuracy and the highest ROC AUC, making it highly reliable at distinguishing between funding outcomes.

**Feature Importances:**
1. `average_pledge_per_backer`: 53.94%
2. `goal`: 19.05%
3. `subcategory_success_rate`: 11.89%
4. `category_success_rate`: 6.00%
5. `goal_realism_score`: 5.74%
6. `competition_density`: 3.37%

Similar to the Random Forest model, the monetary dynamics (`average_pledge_per_backer` and `goal`) completely dominate the decision tree splits. The gradient boosting approach placed slightly higher emphasis on raw structural features over computed ratios compared to the Random Forest model.

**Model Artifact Output:**
- The trained XGBoost model is successfully saved at: `src/models/kickstarter_xgboost_model.pkl`

---

## Project Planning Update

As the Kickstarter Viability Analyzer has successfully completed its core Data Pipeline and Model Training phases (Logistic Regression, Random Forest, XGBoost), the project roadmap has evolved. 

The original `AGENT_TASK_TREE_v2` has been superseded by `AGENT_TASK_TREE_v3`, which is located in `specs/AGENT_TASK_TREE_v3.md`. This new task tree clearly separates the completed phases from the upcoming work:

1. **Prediction / Inference Pipeline:** Building the pre-launch prediction engine and goal optimization logic using our trained XGBoost model.
2. **API Layer:** Exposing the prediction and optimization capabilities via REST endpoints.
3. **Web Demo:** Building the final user interface where users can input their planned Kickstarter parameters and receive a predicted probability of success.

Future development agents should refer to `AGENT_TASK_TREE_v3` for the remaining tasks.

---

## Phase 4 — Pre-Launch Prediction Model - AGENT_TASK_TREE_v3.md

**Objective:**
To build the actual model to be used by the web demo. This prediction engine estimates a project's probability of success using *only* information available *before* a campaign goes live.

**The Data Leakage Issue:**
Previous models (Phases 4-6 of `AGENT_TASK_TREE_v2`) utilized the feature `average_pledge_per_backer`. This was highly predictive but introduced **data leakage**, as this metric requires the campaign to be actively running and accumulating backers. To provide true pre-launch estimates, post-launch metrics must be strictly excluded.

**Features Used:**
Given the strict pre-launch bounds, only the following structural and historical metrics are supplied to the predictor:
- `goal`
- `goal_realism_score`
- `category_success_rate`
- `subcategory_success_rate`
- `competition_density`

*(Explicitly Excluded: `average_pledge_per_backer`)*

**Evaluation Metrics (Test Set):**
Because we removed the most heavily weighted feature from the tree splits (60% importance in earlier models), performance naturally degrades:
- **Accuracy:** 0.6892
- **ROC AUC:** 0.7218

This represents the realistic predictive ceiling before a campaign begins acquiring backers. 

**Feature Importances:**
Without post-launch pledge velocity masking the tree layers, the categorical historical success rates became the primary survival indicators:
1. `subcategory_success_rate`: 46.58%
2. `goal`: 20.00%
3. `category_success_rate`: 15.62%
4. `goal_realism_score`: 13.13%
5. `competition_density`: 4.67%

**Model Artifact Output:**
- The trained XGBoost launch predictor is saved at: `src/models/kickstarter_launch_predictor.pkl`

### Temporal Feature Engineering Improvement

**Objective:**
To improve the pre-launch predictive capability by capturing seasonality and campaign timing effects without introducing data leakage. 

**Features Added:**
Because the specific timing of a Kickstarter launch strongly impacts initial traction, we derived three new purely temporal features based on the known pre-launch timestamp properties:
- `launch_month` (1-12)
- `launch_day_of_week` (0-6)
- `campaign_duration` (Difference in days between deadline and launch)

**Evaluation Metrics (Test Set):**
By incorporating temporal properties, the model successfully mapped seasonality signals:
- **Accuracy:** 0.7032 *(+0.0140 improvement)*
- **ROC AUC:** 0.7443 *(+0.0225 improvement)*

**Feature Importances:**
The new feature `campaign_duration` captured roughly 12.67% of predictive importance, indicating that the length of the pledging period heavily impacts the structural viability of a project:
1. `subcategory_success_rate`: 37.58%
2. `goal`: 17.30%
3. `goal_realism_score`: 12.67%
4. `campaign_duration`: 12.67%
5. `category_success_rate`: 7.85%
6. `competition_density`: 5.10%
7. `launch_day_of_week`: 3.54%
8. `launch_month`: 3.29%

### Prediction Engine Module

**Objective:**
To build a reusable prediction inference module that bridges the gap between raw user input and the trained Machine Learning features. 

**Implementation Details (`src/prediction/predictor.py`):**
1. **Model Loading:** The script utilizes `joblib` to lazily load `kickstarter_launch_predictor.pkl` directly into memory on the first execution, preventing constant I/O bottlenecks.
2. **Feature Mapping:** Because the XGBoost model expects an exact array input order, the `build_feature_vector(project_inputs)` function sanitizes dictionary keys, guarantees numeric typing, and rigidly packages the metrics into an ordered 2D numpy array:
   `[goal, goal_realism_score, category_success_rate, subcategory_success_rate, competition_density, launch_month, launch_day_of_week, campaign_duration]`
3. **Inference Generation:** The `predict_success_probability()` function feeds the mapped array into `model.predict_proba()` to extract the explicit probability of class 1 ("Successful"), providing both the float evaluation and the string-classified class designation.

**CLI Validation:** running `python -m prediction.predictor` successfully unpacks a dummy dictionary containing real-world representations of feature bounds. The test configuration generated a `60.24%` pre-launch success probability projection.

### Goal Optimization Logic

**Objective:**
To build a companion simulation module that evaluates multiple possible structural funding goals around a user's defined base goal and mathematically suggests the target that maximizes the overall probability of Kickstarter success.

**Implementation Details (`src/prediction/goal_optimizer.py`):**
1. **Candidate Generation:** The `generate_goal_candidates(base_goal)` function establishes a search radius from roughly 30% to 200% of the input value. It generates 20 evenly spaced candidates and rounds them to clean increments (e.g., nearest 100) to keep monetary values realistic.
2. **Simulation Loop:** The `optimize_goal(project_inputs)` procedure performs a deep copy of the raw project features, substitutes the iterating candidate goals in place of the base goal, and repetitively queries the central `predict_success_probability()` ML engine.
3. **Execution Delivery:** The iteration loop tracks the simulated success outputs per goal configuration and returns an aggregated JSON payload dictating:
   - The original/optimal prediction mapping
   - `optimal_goal`: The goal that reached maximal probability
   - `optimal_probability`: The statistical height reached
   - `goal_analysis`: The entire list of simulated increments for charting.

**CLI Validation:** When running `python -m prediction.goal_optimizer` against a baseline $15,000 project (evaluating at `60.24%`), the optimizer correctly tracked 20 simulated adjustments between $4500 and $30k and recommended safely dropping the funding goal to **$8500**, which pushed the survival metric up to **62.40%**. 

This feature will act as the primary recommendation mechanic behind the impending **Web Demo** interface.

### Feature Contribution Breakdown

**Objective:**
To build a machine learning explainability layer that deconstructs the `XGBClassifier`'s black-box probability output and attributes concrete credit/blame to individual user inputs, helping users understand exactly *why* their campaign was rated a certain way.

**Implementation Details (`src/prediction/explainer.py`):**
1. **SHAP Integration:** The module utilizes the `shap` repository, initializing a `TreeExplainer` around the cached XGBoost prediction tree.
2. **Probability Deconstruction:** The `explain_prediction()` function evaluates the strict mathematical log-odds contribution of every single dimension inside the mapped 2D input array. 
3. **Engine Bridge:** The core `predictor.py` interface was augmented with an optional `include_contributions` boolean that silently routes the `project_inputs` dict through the SHAP explainer and appends a `feature_contributions` JSON object to the payload if requested by the end-user.

**CLI Validation:** Running `python -m prediction.explainer` successfully proved model explainability and sorted outputted feature impacts by absolute magnitude. For the tested $15k dummy payload, the campaign's 30-day duration carried the project with a massive **+0.5637** positive log-odd impact, whereas the dense competition within the chosen subcategory dragged the final probability down by **-0.0355**.

This explainability layer fulfills `TASK-035` and provides the final contextual pillar necessary for building the overarching `/predict` API interface.

---

## Phase 5 — API Layer

**Objective:**
To build out a robust REST interface using FastAPI that bridges the centralized Python codebase over to the front-end Web Demo, exposing the trained machine learning pipelines to standard HTTP methodologies.

**Implementation Details (`src/api/`):**
1. **API Architecture:** The server operates on ASGI (`uvicorn`) and leverages `FastAPI` to provide auto-generated OpenAPI documentation and high-performance routing. CORS middleware was configured to permit local browser integration.
2. **Endpoint Structure (`/predict`):** 
   - Receives POST requests defined by the strict static `ProjectInput` pydantic schema (`schemas.py`), ensuring that only valid, syntactically correct inputs (`goal`, `category`, `subcategory`, `launch_month`, `launch_day_of_week`, `campaign_duration`) are processed.
3. **Integration with Prediction Engine:** 
   - **Lifespan Cache:** Because the `XGBClassifier` demands explicit subcategory success rates and realistic goal metrics, the API launches a localized dictionary cache during the `@asynccontextmanager` startup phase. It calls the original `build_analytics_features()` database ingestion, storing relational lookup stats directly in memory.
   - **Inference Pipeline:** When a payload hits `/predict`, the API resolves the user strings against the global statistics cache to formulate a flawless 8-dimensional numeric metric array. It then feeds the payload simultaneously to:
     1. `predict_success_probability()` (extracting the survival odds and class designation)
     2. `optimize_goal()` (extracting 20-candidate optimization increments)
     3. `explain_prediction()` (extracting SHAP feature impacts via log-odds)
   - It collates the responses into a universally consumable JSON blob.

**CLI Validation:** The server was configured and validated using `uvicorn api.app:app --reload`. The system safely pre-computed the subcategory database map within 4 seconds, hosted on `http://127.0.0.1:8000/docs`, and exposed the interactive Swagger console for direct user metric adjustments.

### Prediction API — Goal Optimization Endpoint

**Objective:**
To expose goal optimization as a standalone, dedicated service endpoint (`/optimize`). This allows clients to independently request strategic goal recommendations and mathematically evaluate their chances of success without fetching the full prediction pipeline.

**Integration Details (`src/api/app.py`):**
1. **Endpoint Location:** The POST `/optimize` route accepts the exact same structured `ProjectInput` Pydantic payload as `/predict`.
2. **Architecture Integration:** By reusing the identical pre-loaded XGBoost cache and analytics data, the API bypasses expensive I/O operations and instantly evaluates the prediction logic.
3. **Execution Workflow:** 
   - `_map_to_model_features(payload)` parses the JSON.
   - The route initially queries the current Baseline success probability.
   - It executes `optimize_goal()` to iteratively generate candidates and deduce the mathematical maximum probability achievable for the project's subcategory.
4. **Structured JSON Output:**
   - Instead of a massive intelligence payload, the endpoint delivers a direct recommendation containing:
     - `original_goal`
     - `recommended_goal`
     - `expected_success_probability`
     - `improvement_over_original`

**Example Request Payload:**
```json
{
  "goal": 15000,
  "category": "Technology",
  "subcategory": "Gadgets",
  "launch_month": 5,
  "launch_day_of_week": 2,
  "campaign_duration": 30
}
```

**Example JSON Response:**
```json
{
  "original_goal": 15000.0,
  "recommended_goal": 8500.0,
  "expected_success_probability": 0.624,
  "improvement_over_original": 0.0216
}
```

---

## Phase 6 — Web Demo (Streamlit)

**Objective:**
To build a lightweight interactive web demo using Streamlit that consumes the existing FastAPI endpoints, allowing users to input project parameters and receive predictions.

**Implementation Details (`demo/streamlit_app.py`):**
1. **UI Architecture**: Structured into four logical sections for Project Inputs, Prediction Results, Goal Optimization, and Feature Explanation.
2. **API Integration**: Uses the `requests` library to interface with the local `http://localhost:8000` REST API. Safely catches connection errors if the server is offline.
3. **User Interaction Flow**: Provides interactive widgets (dropdowns, sliders, number inputs) to map out campaign goals and categorical parameters. Upon form submission, it queries both `/predict` and `/optimize` endpoints.
4. **Visualization**: Extracts the SHAP log-odds feature contributions from the prediction response and dynamically sorts them into a Streamlit bar chart, mapped for positive and negative impacts.

**Local Execution Instructions:**
1) Start the API server:
   `uvicorn src.api.app:app --reload`

2) Start the Streamlit demo:
   `streamlit run demo/streamlit_app.py`

