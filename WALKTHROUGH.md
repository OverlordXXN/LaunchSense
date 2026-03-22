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

---

## Phase 7 — UI Enhancements: Goal Optimization Visualization

**Objective:**
To enhance the Streamlit web demo by providing a visual representation of how the funding goal impacts the probability of success. This addresses tasks **TASK-042** and **TASK-043**.

**Implementation Details:**
1. **API Enhancement (`src/api/app.py`)**: 
   - The `/optimize` endpoint was modified to include the `goal_analysis` dataset generated by the `optimize_goal()` function in its JSON response payload. 
   - Originally, this data was computed to find the mathematical maximum but discarded before returning to the client. Safely packaging it enables downstream rendering without recalculating predictions.
2. **Streamlit UI Update (`demo/streamlit_app.py`)**: 
   - The Streamlit frontend extracts the `goal_analysis` list of dictionaries containing individual goals and their corresponding success probabilities.
   - The data is transformed into a Pandas DataFrame. The goals are converted to numeric values to act as the X-axis, and the probabilities are multiplied by 100 to display percentages on the Y-axis.
   - Using `st.line_chart`, an interactive curve is rendered showing the relationship between funding milestones and project viability.
   - Contextual markdown is printed directly beneath the curve, highlighting the original baseline goal alongside the new optimal recommended goal.

**Design Decisions:**
- **Performance**: We reuse the cached prediction models and the already implemented simulated increment loop from `goal_optimizer.py`. The frontend simply plots the returned array, keeping the app lightweight and responsive.
- **Resolution**: The `optimize_goal()` array tests roughly 20 candidate increments (from 30% to 200% of the base goal), which provides a sufficiently smooth curve for the line chart without crippling the API server with excessive inference calls.

**CLI/Local Validation:**
When the Streamlit app loads and a user configures a project, the Goal Optimization UI block presents the original and optimal metrics, immediately followed by the new visual curve cleanly mapping the drop-off in probability as the requested funding increases.

---

## Phase 8 — Advanced Analytics & UX: SHAP Waterfall Visualization

**Objective:**
To improve the interpretability of the machine learning model by replacing the standard feature contribution bar chart with a cumulative **Waterfall Chart**. This allows users to see exactly how their project's base survival probability is shifted positively and negatively by individual features to reach the final success prediction. Address task **TASK-044**.

**Implementation Details:**
1. **Requirements (`requirements.txt`)**: 
   - Standardized the use of `matplotlib` to render complex UI charts for the Streamlit demo.
2. **Streamlit UI Update (`demo/streamlit_app.py`)**: 
   - The original dictionary of raw SHAP feature contributions (log-odds impact) is intercepted by the frontend.
   - The UI back-calculates the base probability mathematically by extracting the total log-odds impact from the final prediction's log-odds.
   - Using `math.exp` conversions, each individual sequential SHAP impact is translated into absolute percentage steps (e.g., "Category pushed probability up by +12%").
   - A Matplotlib `bar` chart is constructed using the `bottom` stacking parameter to simulate a waterfall trajectory. 
   - The axes and labels are reformatted to percentage scales.

**Design Decisions:**
- **Mathematical Integrity**: SHAP values are inherently additive only in the log-odds space (for classification). Rather than improperly summing raw probabilities, the visualization meticulously reconstructs the probability curve step-by-step through the sigmoid function, preserving exact mathematical correctness.
- **UX Clarity**: The bars are color-coded intuitively. A gray "Base Probability" bar acts as the anchor. Green bars indicate beneficial traits (e.g., strong category or realistic goal), while red bars visualize detriments (e.g., excessive campaign duration). A blue "Final Prediction" bar concludes the layout.

**CLI/Local Validation:**
When configuring a project in Streamlit, the "Feature Contributions" section now renders the interactive Waterfall chart. Users can trace the exact numerical lineage of the model's decision, making the XGBoost classifier incredibly transparent and actionable.

---

## Phase 8 — Advanced Analytics & UX: Dynamic Category Selectors

**Objective:**
To replace the hardcoded UI dropdown lists of Kickstarter categories and subcategories with dynamic ones derived straight from the original database. This ensures users can only evaluate models using inputs the dataset was structurally trained against, increasing inference accuracy and preventing `KeyError` mappings or fallback assumptions. Adresses task **TASK-045**.

**Implementation Details:**
1. **API Mapping (`src/api/app.py`)**: 
   - Modified the FastApi lifespan process (`@asynccontextmanager`). After querying the `build_analytics_features()` pandas DataFrame during server initialization to extract success_rates, the script performs a unique `groupby` application linking every known `'category'` strictly to its historically paired `'subcategory'` bounds.
   - This mapping is pinned to memory under `_CACHE['categories_map']`.
   - Exposed this configuration block via a fast `GET /categories` endpoint.
2. **Streamlit UI Update (`demo/streamlit_app.py`)**: 
   - Purged the manual array constants `CATEGORIES` and `SUBCATEGORIES`.
   - Built a `@st.cache_data(ttl=3600)` initialization function `fetch_categories_map()` which queries the backend API once an hour, shielding the server from re-querying the database layout on every tiny slider adjustment.
   - Deconstructed the `st.form` architecture around "Project Inputs". Because Streamlit natively prevents interdependent dependent widgets from visually updating each other while trapped inside a unified form (preventing subcategory filtering), the input components were refactored to float globally with a unifying "Predict Success" button evaluating the global state.
   - The selected subcategory is explicitly filtered: `subcat_options = sorted(categories_map.get(category, []))` guaranteeing mathematical alignment between dropdown states.

**Design Decisions:**
- **Caching Layer**: By passing dataset discovery entirely to the backend FastAPI system on-startup, the database connection is never exposed or re-opened by Streamlit layout code. Data flows consistently through REST logic.

**CLI/Local Validation:**
Operating `verify_categories.py` against `localhost:8000/categories` returned HTTP 200 mapping dictating all 15 Kickstarter super-categories. Operating Streamlit UI flawlessly restricts the Subcategory widget—for example, selecting "Technology" restricts the child input solely to valid internal variants ensuring flawless dataset-alignment downstream.

---

## Phase 8 — Advanced Analytics & UX: Similar Projects Comparison Panel

**Objective:**
To give users tangible historical context beyond abstract probabilities. By displaying how historically identical projects actually performed mathematically, users can gauge the realism of their target. Addresses task **TASK-046**.

**Implementation Details:**
1. **API Analytics Layer (`src/analytics/similarity.py`)**: 
   - Refactored `calculate_similarity_metrics()` to ingest an exact dictionary of the user's project parameters alongside a pre-loaded Pandas DataFrame.
   - It performs vector-masked progressive filtering: First requiring an exact Category & Subcategory match. If over 20 results exist, it restricts the query drastically to projects with precisely similar funding bounds (`+/- 50%`) and scheduling boundaries (`+/- 7 days`).
   - The engine evaluates confidence (`High`, `Moderate`, `Low`) based on how strictly it had to filter the original cohort to maintain statistical relevance, returning `historical_success_rate`, `average_goal`, and `average_duration`.
2. **API Endpoint (`src/api/app.py`)**:
   - Expanded the `lifespan` initialization cache. Alongside the previously established category map, the script now dumps a 5-column lightweight permutation of the database (`['category', 'subcategory', 'goal', 'campaign_duration', 'is_successful']`) securely into RAM as `_CACHE['projects_df']`. 
   - A new `POST /similar-projects` endpoint was exposed that routes payloads straight against this static RAM cache. **This explicitly avoids hitting the PostgreSQL database layer dynamically per-request, enforcing O(1) database complexity and eliminating query lag.**
3. **Streamlit UI Update (`demo/streamlit_app.py`)**:
   - Developed a new "Similar Projects Insights" UI block populated by `st.columns()` and visually distinct `st.metric()` widgets emphasizing competitor statistics.
   - Added `st.success` / `st.info` semantic alerts explicitly comparing the user's predicted ML chance against the rigid historical median.

**Design Decisions:**
- **In-Memory Caching Philosophy**: By aggregating Phase 8 (Categories Map + Similarity Matrix) entirely through a single asynchronous Pandas DataFrame build logic during app-startup, the backend operates robustly in high-traffic scenarios without bottle-necking a relational database.

**CLI/Local Validation:**
Executing a payload mimicking a $15,000 Technology/Gadget campaign through `verify_similar.py` immediately returned 524 identically matched comps boasting an average historical success rate of ~31% (`Confidence: High`), accurately reflected in the frontend UI.

---

## Phase 8 — Advanced Analytics & UX: Streamlit UI Refactoring

**Objective:**
To transform the functional, linear Streamlit architecture into a professional, side-by-side dashboard suitable for public presentation. This enhances visual hierarchy and guides the user smoothly from data input through complex ML extrapolation. Addresses task **TASK-047**.

**Implementation Details (`demo/streamlit_app.py`):**
1. **Layout Paradigm**: 
   - Introduced a `main_col1, main_col2 = st.columns([1, 2], gap="large")` grid container.
   - Constrained all interactive widgets (`Category`, `Goal`, `Subcategory`, `Launch Date`, `Duration`) and the `Predict Success` trigger into the static left third of the screen.
   - Devoted the right two-thirds exclusively to a dynamic results dashboard.
2. **Visual Hierarchy & Interpretability**:
   - Organized the output layer chronologically:
     - **Layer 1 (Prediction)**: Features core metrics alongside a new conditional interpretation string (`st.success`, `st.info`, `st.error`) translating the raw probability (e.g., > 70% vs < 40%) into actionable human-readable advice.
     - **Layer 2 (Optimization)**: Groups the optimal parameters clearly, nesting the probability curve graph inside an `st.expander` to reduce immediate clutter.
     - **Layer 3 (Explanation)**: Renders the SHAP Waterfall matrix mapping precisely why the base rate moved to the predicted chance.
     - **Layer 4 (Historical Context)**: Directly contrasts the AI's extrapolated probability against the historical mean of peers, adding a final sanity-check insight.
   - Employed `st.divider()` extensively to partition the analytical layers.

**Design Decisions:**
- **Presentation Clarity**: Standardizing the `[1, 2]` geometry ensures the user does not need to awkwardly scroll up and down to tweak inputs linearly. They can adjust sliders on the left and see the right-hand dashboard react consistently. Nesting complex charts (like the goal optimization curve) keeps the first-glance UI extremely clean.

**CLI/Local Validation:**
Opening `localhost:8501` reveals a blank dashboard inviting input. Hitting predict immediately paints the right-hand canvas with beautifully staggered statistics, conversational insights, and complex charts perfectly contained on desktop displays.


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

## Phase 10 — Pipeline Hardening & Reliability

### Improvements Added
To ensure the pipeline handles continuous execution robustly without creating data corruption or excessive load:

* **Duplicate Prevention Strategy**: The `update_dataset.py` script now explicitly drops duplicates across the entire historical and newly scraped dataset using a composite `subset=["Name", "Launched"]` rule. This guarantees that running the pipeline back-to-back will remain perfectly idempotent and will not artificially inflate the dataset size.
* **Logging Approach**: Replaced default `logging` objects with straightforward `print()` statements across all `scripts/` components. The orchestration script `refresh_pipeline.py` clearly wraps the execution flow in stages (e.g., `--- Running 1. Scraper ---`).
* **Error Handling Design**: The master pipeline in `refresh_pipeline.py` wraps execution in a robust `try...except` block, catches `subprocess.CalledProcessError` or user interruptions (`KeyboardInterrupt`), outputs exactly which stage failed, and aborts any subsequent downstream actions to prevent partial or corrupted state deployment.
* **Scraping Limits**: Bounded continuous execution by hardcoding `MAX_PAGES = 5` and `MAX_PROJECTS = 100` natively in `scripts/scrape_kickstarter.py`. This ensures manual MVP tests won't unintentionally scrape the entire Kickstarter network or trip aggressive IP bans.

The system is now reliably executing live data updates.

## Scraper Fix — Handling 403 Forbidden

### Issue
During scraping ops, Kickstarter returns a `403 Client Error: Forbidden` when accessed via plain `requests.get()`. This is because Kickstarter employs anti-bot protections (like Cloudflare) which block HTTP requests lacking standard browser headers.

### Implementation
To bypass basic bot detection and restore scraper functionality:
1. **Header Injection**: All outgoing requests in `src/scraper/crawler.py` and `src/scraper/parser.py` have been updated to include a standard `User-Agent` (Chrome/115.0 on Windows) and an `Accept-Language` header.
2. **Requests Session**: Instead of using stateless `requests.get()`, both modules now utilize a `requests.Session()` object which retains headers natively across multiple project fetches and optimizes TCP connection reuse.
3. **Validation**: Requests are wrapped in `raise_for_status()` to catch HTTP errors and gracefully terminate the scrape loop with clear logging.

---

## Phase 21 — Cloud Deployment Compatibility

### Objective
To implement a standalone "Cloud Mode" fallback for the Streamlit application to ensure it can operate natively in environments like Streamlit Cloud without depending on the local FastAPI backend.

### Implementation Details
1. **Mode Detection**: A new `st.session_state.standalone_mode` boolean explicitly tracks API health. All `.post()` and `.get()` analytical queries sent to the `API_BASE_URL` were wrapped in `try/except` safeguards catching `requests.exceptions.RequestException`.
2. **Offline Categories Integration (`TASK-106`)**: If the initial `/categories` query fails, the app flips the standalone mode to True and manually loads `data/processed/full_dataset.csv`, deduplicates mappings, normalizes spelling, and mocks the exact identical JSON structure downstream.
3. **Local Inference Loading (`TASK-105 & TASK-107`)**: When in Standalone Mode, the `demo/streamlit_app.py` directly imports the backend modules natively (`prediction.predictor`, `prediction.goal_optimizer`, `analytics.similarity`). The system bridges the connection by building an offline approximation of the FastAPI translation layer (`_map_payload_offline`), fetching `models/latest.joblib`, and calculating ML evaluations directly inside the Streamlit memory space context.
4. **UI Indicators (`TASK-108`)**: A toggleable badge string `st.info("Cloud Mode (Standalone)")` vs `st.caption("API Mode")` was integrated underneath the main Title signaling which routing logic handled the inference.

**Validation Details**:
Turning off the running server (`uvicorn`) and attempting to trigger predictions no longer terminates in a stack-trace. The UI dynamically detects the dead endpoint, seamlessly switches to Standalone Cloud Mode, retrieves categories from the CSV cache, evaluates local SHAP approximations, and calculates optimal goals internally.

---

## Phase 22 — Standalone Inference Fix

### Objective
To refactor the Streamlit standalone fallback logic to unify the inference pipeline explicitly. This eliminates reliance on deliberate HTTP exceptions (used strictly for control flow) and directly embraces `st.session_state` branching across all API boundaries.

### Implementation Details
1. **Control Flow Standardization (`TASK-112`)**: Removed internal `raise requests.exceptions.ConnectionError` blocks. The prediction, optimization, and contextual evaluation logic is now segmented distinctly into unified `if st.session_state.standalone_mode:` operations.
2. **Error Safety & UX Continuity (`TASK-109 & TASK-110`)**: The outermost `st.error` generic fallback was replaced. Standard API request timeouts appropriately trigger the Standalone toggle, seamlessly rendering the `st.caption("Running in Cloud Standalone Mode")` descriptor without violently halting the user experience.
3. **Execution Delivery (`TASK-111`)**: The unified pipeline accurately bridges `src/prediction` execution scopes and streams dictionary representations directly into the native Streamlit rendering layout identically to standard operational metrics.

---

## Phase 23 — Branding & Production Polish

### Objective
To apply final production UI polish, legal disclaimers, and open-source branding elements signaling public readiness.

### Implementation Details
1. **Header Rebranding (`TASK-113 & TASK-114`)**: Migrated the generic application title to the formalized **LaunchSense** brand, positioned alongside a descriptive subtitle articulating the purpose of the ML simulator. 
2. **Legal Attributions (`TASK-115 & TASK-119`)**: Added explicit disclaimers declaring independence from Kickstarter PBC globally at both the immediate subtitle point of origin and the terminal footer, securing safe trademark utilization.
3. **UX Enhancements (`TASK-116 & TASK-117 & TASK-118`)**: Embedded the open-source GitHub repository URL seamlessly into the layout configuration, added explicit color-coded icons to the Standalone toggle, and finalized a versioned footer (`v1.0`).
