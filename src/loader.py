"""
loader.py — Stage 4: Load
Idempotent bulk loader into SQLite (demo) / PostgreSQL (prod).
Uses INSERT OR IGNORE to prevent duplicates on re-runs.
Supports rollback on failure.
"""

import sqlite3
from pathlib import Path

SCHEMA_FILE = Path(__file__).parent.parent / "sql" / "schema.sql"

# ── Column definitions per target ────────────────────────
COLUMNS = {
    "ar_records":     ["invoice_id", "customer_name", "amount", "currency", "due_date", "status", "created_at"],
    "ap_records":     ["bill_id", "vendor_name", "amount", "currency", "due_date", "payment_status", "created_at"],
    "vendor_records": ["vendor_id", "vendor_name", "contact_email", "phone", "payment_terms", "currency", "active"],
}


def init_db(db_path: str = "pipeline.db") -> None:
    """Create tables from schema.sql if they don't exist."""
    schema_sql = SCHEMA_FILE.read_text()
    with sqlite3.connect(db_path) as conn:
        conn.executescript(schema_sql)


def load_records(records: list[dict], target: str, db_path: str = "pipeline.db") -> int:
    """
    Bulk-insert records into `target` table.
    INSERT OR IGNORE makes the operation idempotent (safe to re-run).
    Wraps everything in a transaction — rolls back on any error.
    Returns count of successfully inserted rows.
    """
    cols = COLUMNS.get(target)
    if not cols:
        raise ValueError(f"Unknown target table: {target}")

    placeholders = ", ".join(["?"] * len(cols))
    col_list     = ", ".join(cols)
    sql          = f"INSERT OR IGNORE INTO {target} ({col_list}) VALUES ({placeholders})"

    rows = [[r.get(c) for c in cols] for r in records]

    try:
        with sqlite3.connect(db_path) as conn:
            conn.execute("PRAGMA journal_mode=WAL;")  # safer writes
            cursor = conn.executemany(sql, rows)
            inserted = cursor.rowcount
            conn.commit()
        return inserted
    except Exception as e:
        print(f"\n  [ERROR] Load failed, rolling back: {e}")
        raise


def log_migration(run_id: str, target: str, source_file: str,
                  source_count: int, valid_count: int,
                  error_count: int, loaded_count: int,
                  status: str, db_path: str = "pipeline.db") -> None:
    """Append a migration run record to the audit log."""
    sql = """
        INSERT INTO migration_log
          (run_id, target, source_file, source_count, valid_count, error_count, loaded_count, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """
    with sqlite3.connect(db_path) as conn:
        conn.execute(sql, (run_id, target, source_file,
                           source_count, valid_count,
                           error_count, loaded_count, status))
        conn.commit()
