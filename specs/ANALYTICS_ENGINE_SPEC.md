# ANALYTICS_ENGINE_SPEC.md

## Project

Kickstarter Funding Viability Analyzer

## Purpose

This document defines the analytics engine responsible for generating
insights, statistics, and predictive models based on Kickstarter project
data.

The analytics engine consumes normalized project data stored in
PostgreSQL and produces analytical outputs used by: - the demo web
application - internal evaluation tools - ML training pipelines

The analytics layer should be modular and callable via Python functions.

------------------------------------------------------------------------

# 1. ENGINE OBJECTIVES

The analytics engine must provide the ability to:

1.  Analyze historical Kickstarter funding data
2.  Identify comparable projects
3.  Compute descriptive statistics
4.  Estimate funding velocity
5.  Estimate time to reach funding goal
6.  Estimate probability of success
7.  Provide structured insights for UI consumption

------------------------------------------------------------------------

# 2. MODULE LOCATION

The analytics engine should be implemented in:

src/analytics/

Recommended structure:

src/analytics/ │ ├── **init**.py ├── similarity.py ├── statistics.py ├──
funding_analysis.py ├── prediction.py └── analytics_service.py

------------------------------------------------------------------------

# 3. DATA INPUT

Primary data source: PostgreSQL database populated by: - Kaggle dataset
ingestion - Kickstarter scraper

Main tables used:

projects project_snapshots categories pledge_tiers

The analytics engine must assume: - Data may contain missing values -
Schema may evolve - Historical and scraped data may differ in format

The engine should normalize fields internally where necessary.

------------------------------------------------------------------------

# 4. CORE ANALYTICS FUNCTIONS

## Find Similar Projects

Function: find_similar_projects(input_project_features)

Input example:

{ category: "board games", goal: 50000, duration_days: 30, country: "US"
}

Similarity criteria: - category - goal range - duration - country
(optional)

Return top N matches.

------------------------------------------------------------------------

# 5. STATISTICAL ANALYSIS

Median goal: median(goal)

Median funding: median(pledged)

Median backers: median(backers)

Average pledge per backer: avg_pledge = pledged / backers

------------------------------------------------------------------------

# 6. FUNDING VELOCITY

Definition: funding_velocity = pledged / duration_days

Aggregations: - median velocity - mean velocity - distribution

------------------------------------------------------------------------

# 7. TIME TO GOAL ESTIMATION

Estimate: time_to_goal = goal / funding_velocity

Return: - median_days_to_goal - mean_days_to_goal

------------------------------------------------------------------------

# 8. SUCCESS RATE

success_rate = successful_projects / total_projects

Function: compute_success_rate(similar_projects)

------------------------------------------------------------------------

# 9. MACHINE LEARNING MODEL

Goal: Predict probability that a project will successfully reach its
funding goal.

Initial model: Logistic Regression

Possible future upgrades: - Gradient Boosting - Random Forest

Training features: goal category duration country launch_year

Target: successful (0/1)

Function: predict_success_probability(project_features)

Output: probability_success ∈ \[0,1\]

------------------------------------------------------------------------

# 10. ANALYTICS SERVICE

High-level function:

analyze_project(project_features)

Example input:

{ category: "board games", goal: 50000, duration_days: 30, country: "US"
}

Example output:

{ success_probability: 0.68, median_goal: 42000, median_funding: 51000,
median_backers: 320, avg_pledge: 64, success_rate: 0.62,
median_days_to_goal: 21 }

------------------------------------------------------------------------

# 11. PERFORMANCE REQUIREMENTS

-   Support datasets up to \~500k projects
-   Typical response \< 2 seconds
-   Prefer indexed queries
-   Avoid full table scans

------------------------------------------------------------------------

# 12. FUTURE ANALYTICS EXTENSIONS

Possible future features:

-   Category growth trends
-   Geographic funding patterns
-   Reward tier impact analysis
-   Launch timing analysis

------------------------------------------------------------------------

# 13. ERROR HANDLING

Analytics functions must: - handle missing values - return default
metrics when insufficient data exists - log warnings for incomplete
datasets

------------------------------------------------------------------------

# 14. TESTING

Tests must validate: - statistical correctness - stable output schema -
behavior with small datasets - handling of missing values

------------------------------------------------------------------------

# 15. OUTPUT FORMAT

All analytics results must return JSON-compatible dictionaries.
