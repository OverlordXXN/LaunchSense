# AGENT_TASK_TREE_v2
Kickstarter Viability Analyzer

Total tasks: 40

------------------------------------------------
PHASE 1 — PROJECT SETUP
------------------------------------------------

TASK-001 setup logging module
TASK-002 implement config loader
TASK-003 implement project path utilities
TASK-004 setup environment variables
TASK-005 implement PostgreSQL connection

------------------------------------------------
PHASE 2 — HISTORICAL DATA INGESTION
------------------------------------------------

TASK-006 load Kaggle dataset
TASK-007 inspect dataset schema
TASK-008 normalize column names
TASK-009 convert date columns
TASK-010 compute project duration
TASK-011 compute success label
TASK-012 save cleaned dataset

------------------------------------------------
PHASE 3 — DATABASE
------------------------------------------------

TASK-013 create database schema
TASK-014 create projects table
TASK-015 create project_snapshots table
TASK-016 implement DB insertion utilities
TASK-017 implement duplicate detection

------------------------------------------------
PHASE 4 — SCRAPER
------------------------------------------------

TASK-018 implement discover page crawler
TASK-019 collect project URLs
TASK-020 scrape project pages
TASK-021 extract project metadata
TASK-022 extract funding metrics
TASK-023 parse embedded JSON data
TASK-024 store project snapshots
TASK-025 implement rate limiting

------------------------------------------------
PHASE 5 — DATA NORMALIZATION
------------------------------------------------

TASK-026 unify Kaggle and scraped schemas
TASK-027 normalize currencies
TASK-028 compute funding ratio
TASK-029 compute pledge per backer
TASK-030 compute funding velocity

------------------------------------------------
PHASE 6 — ANALYTICS ENGINE
------------------------------------------------

TASK-031 implement similar project search
TASK-032 compute category statistics
TASK-033 compute funding velocity statistics
TASK-034 implement time-to-goal estimator
TASK-035 implement success probability model

------------------------------------------------
PHASE 7 — API
------------------------------------------------

TASK-036 implement analytics API
TASK-037 implement similarity endpoint
TASK-038 implement viability endpoint

------------------------------------------------
PHASE 8 — WEB DEMO
------------------------------------------------

TASK-039 build demo interface
TASK-040 display analytics results