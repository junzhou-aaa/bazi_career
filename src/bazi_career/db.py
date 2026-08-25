import sqlite3
import json
from pathlib import Path
from contextlib import contextmanager
from .config import DB_PATH, DATA_DIR

SCHEMA = """
CREATE TABLE IF NOT EXISTS profiles (
    id TEXT PRIMARY KEY,
    created_at TEXT,
    updated_at TEXT
);

CREATE TABLE IF NOT EXISTS birth_profiles (
    id TEXT PRIMARY KEY,
    profile_id TEXT NOT NULL,
    birth_date TEXT NOT NULL,
    birth_time TEXT,
    birth_time_precision TEXT NOT NULL,
    birth_place_text TEXT,
    timezone TEXT,
    latitude REAL,
    longitude REAL,
    sex TEXT,
    calendar TEXT,
    created_at TEXT,
    updated_at TEXT,
    FOREIGN KEY(profile_id) REFERENCES profiles(id)
);

CREATE TABLE IF NOT EXISTS astrology_models (
    id TEXT PRIMARY KEY,
    profile_id TEXT NOT NULL,
    year_pillar TEXT,
    month_pillar TEXT,
    day_pillar TEXT,
    hour_pillar TEXT,
    day_master TEXT,
    month_order TEXT,
    hidden_stems TEXT, -- JSON
    ten_gods TEXT, -- JSON
    five_elements TEXT, -- JSON
    yin_yang TEXT, -- JSON
    luck_direction TEXT,
    start_of_luck INTEGER,
    luck_cycles TEXT, -- JSON
    model_version TEXT,
    created_at TEXT,
    FOREIGN KEY(profile_id) REFERENCES profiles(id)
);

CREATE TABLE IF NOT EXISTS astrology_predictions (
    id TEXT PRIMARY KEY,
    profile_id TEXT NOT NULL,
    period TEXT,
    domain TEXT,
    claim TEXT,
    traditional_rationale TEXT,
    confidence REAL,
    alternative_explanations TEXT, -- JSON
    created_at TEXT,
    FOREIGN KEY(profile_id) REFERENCES profiles(id)
);

CREATE TABLE IF NOT EXISTS validation_events (
    id TEXT PRIMARY KEY,
    prediction_id TEXT NOT NULL,
    outcome TEXT,
    evidence_statement TEXT,
    created_at TEXT,
    FOREIGN KEY(prediction_id) REFERENCES astrology_predictions(id)
);

CREATE TABLE IF NOT EXISTS calibration_records (
    id TEXT PRIMARY KEY,
    profile_id TEXT NOT NULL,
    hypothesis TEXT,
    evidence_ids TEXT, -- JSON
    prior_confidence REAL,
    posterior_confidence REAL,
    support TEXT, -- JSON
    counterevidence TEXT, -- JSON
    notes TEXT,
    created_at TEXT,
    FOREIGN KEY(profile_id) REFERENCES profiles(id)
);

CREATE TABLE IF NOT EXISTS career_profiles (
    id TEXT PRIMARY KEY,
    profile_id TEXT NOT NULL,
    education TEXT, -- JSON
    experience TEXT, -- JSON
    projects TEXT, -- JSON
    skills TEXT, -- JSON
    programming TEXT, -- JSON
    frameworks TEXT, -- JSON
    cloud TEXT, -- JSON
    languages TEXT, -- JSON
    domain_knowledge TEXT, -- JSON
    communication TEXT, -- JSON
    leadership TEXT, -- JSON
    certifications TEXT, -- JSON
    portfolio_evidence TEXT, -- JSON
    career_identity TEXT, -- JSON
    created_at TEXT,
    updated_at TEXT,
    FOREIGN KEY(profile_id) REFERENCES profiles(id)
);

CREATE TABLE IF NOT EXISTS companies (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    industry_family TEXT,
    size TEXT,
    url TEXT,
    source TEXT,
    source_url TEXT,
    source_last_verified_at TEXT,
    created_at TEXT,
    updated_at TEXT
);

CREATE TABLE IF NOT EXISTS jobs (
    id TEXT PRIMARY KEY,
    company_id TEXT NOT NULL,
    title TEXT NOT NULL,
    role_family TEXT,
    seniority TEXT,
    location TEXT,
    remote_preference TEXT,
    work_authorization_required BOOLEAN,
    sponsorship_available BOOLEAN,
    description TEXT,
    source TEXT,
    source_url TEXT,
    source_last_verified_at TEXT,
    created_at TEXT,
    updated_at TEXT,
    FOREIGN KEY(company_id) REFERENCES companies(id)
);

CREATE TABLE IF NOT EXISTS job_matches (
    id TEXT PRIMARY KEY,
    job_id TEXT NOT NULL,
    profile_id TEXT NOT NULL,
    role_fit_score REAL,
    skill_fit_score REAL,
    industry_fit_score REAL,
    seniority_fit_score REAL,
    location_fit_score REAL,
    work_authorization_fit_score REAL,
    company_fit_score REAL,
    narrative_fit_score REAL,
    total_score REAL,
    tier TEXT,
    rationale TEXT,
    evidence_tier TEXT,
    created_at TEXT,
    FOREIGN KEY(job_id) REFERENCES jobs(id),
    FOREIGN KEY(profile_id) REFERENCES profiles(id)
);

CREATE TABLE IF NOT EXISTS career_plans (
    id TEXT PRIMARY KEY,
    profile_id TEXT NOT NULL,
    content_md TEXT,
    content_json TEXT,
    model_version TEXT,
    prompt_version TEXT,
    taxonomy_version TEXT,
    created_at TEXT,
    FOREIGN KEY(profile_id) REFERENCES profiles(id)
);

CREATE TABLE IF NOT EXISTS config (
    key TEXT PRIMARY KEY,
    value TEXT,
    updated_at TEXT
);
"""

def init_db(db_path: Path | None = None):
    """Initialize the database schema."""
    import bazi_career.db
    path = db_path or bazi_career.db.DB_PATH
    bazi_career.db.DATA_DIR.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(path) as conn:
        conn.executescript(SCHEMA)
        conn.commit()

@contextmanager
def get_db_connection(db_path: Path | None = None):
    """Get a database connection context manager."""
    import bazi_career.db
    path = db_path or bazi_career.db.DB_PATH
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

def set_config(key: str, value: str):
    """Set a configuration value."""
    from datetime import datetime
    with get_db_connection() as conn:
        conn.execute(
            """
            INSERT INTO config (key, value, updated_at) 
            VALUES (?, ?, ?)
            ON CONFLICT(key) DO UPDATE SET 
                value=excluded.value,
                updated_at=excluded.updated_at
            """,
            (key, value, datetime.now().isoformat())
        )
        conn.commit()

def get_config(key: str) -> str | None:
    """Get a configuration value."""
    with get_db_connection() as conn:
        row = conn.execute("SELECT value FROM config WHERE key = ?", (key,)).fetchone()
        return row["value"] if row else None
