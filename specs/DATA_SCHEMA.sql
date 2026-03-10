-- DATA_SCHEMA_v2

CREATE TABLE projects (
    project_id TEXT PRIMARY KEY,
    name TEXT,
    category TEXT,
    subcategory TEXT,
    country TEXT,
    currency TEXT,
    goal NUMERIC,
    created_at TIMESTAMP,
    launched_at TIMESTAMP,
    deadline TIMESTAMP
);

CREATE TABLE project_snapshots (
    snapshot_id SERIAL PRIMARY KEY,
    project_id TEXT REFERENCES projects(project_id),
    snapshot_time TIMESTAMP,
    pledged NUMERIC,
    backers INTEGER,
    state TEXT
);

CREATE TABLE analytics_cache (
    cache_id SERIAL PRIMARY KEY,
    query_hash TEXT,
    result_json JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);