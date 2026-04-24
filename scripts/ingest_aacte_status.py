#!/usr/bin/env python3
"""
ingest_aacte_status.py — Publisher-side AaCT-E status ingestion

Usage:
    python ingest_aacte_status.py --status-file path/to/last_status.json

This script:
1. Parses the AaCT-E CI status report
2. Updates the Publisher dashboard database
3. Triggers social media posts for milestones
4. Archives traces if this is a tagged release
"""

import argparse
import json
import sqlite3
from pathlib import Path
from datetime import datetime, timezone


def init_db(db_path: Path) -> sqlite3.Connection:
    """Initialize SQLite dashboard database."""
    conn = sqlite3.connect(str(db_path))
    conn.execute('''
        CREATE TABLE IF NOT EXISTS aacte_runs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            run_id TEXT UNIQUE,
            commit_sha TEXT,
            repo TEXT,
            status TEXT,
            timestamp_utc TEXT,
            scenario_count INTEGER,
            traces_json TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    return conn


def ingest_status(status_path: Path, db_path: Path) -> None:
    """Ingest a single status report into the dashboard DB."""
    data = json.loads(status_path.read_text(encoding="utf-8"))

    conn = init_db(db_path)
    traces = json.dumps(data.get("traces", []))

    conn.execute('''
        INSERT OR REPLACE INTO aacte_runs
        (run_id, commit_sha, repo, status, timestamp_utc, scenario_count, traces_json)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (
        data.get("run_id"),
        data.get("commit_sha"),
        data.get("repo"),
        data.get("status"),
        data.get("timestamp_utc"),
        len(data.get("traces", [])),
        traces
    ))
    conn.commit()
    conn.close()

    print(f"Ingested run {data.get('run_id')} — {data.get('status')} — {len(data.get('traces', []))} scenarios")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--status-file", type=Path, required=True)
    parser.add_argument("--db", type=Path, default=Path("dashboard.db"))
    args = parser.parse_args()

    ingest_status(args.status_file, args.db)


if __name__ == "__main__":
    main()
