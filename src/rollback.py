#!/usr/bin/env python3
"""
rollback.py — Safe table rollback utility
==========================================
Clears a target table without dropping the schema.
Usage:
  python rollback.py --target ar_records
  python rollback.py --target ar_records --db pipeline.db
"""

import argparse
import sqlite3

VALID_TABLES = ["ar_records", "ap_records", "vendor_records", "migration_log"]


def rollback(target: str, db_path: str = "pipeline.db") -> None:
    if target not in VALID_TABLES:
        print(f"[ERROR] Unknown table: {target}")
        return

    confirm = input(f"⚠  This will DELETE all rows from '{target}'. Type YES to confirm: ")
    if confirm.strip().upper() != "YES":
        print("Rollback cancelled.")
        return

    with sqlite3.connect(db_path) as conn:
        before = conn.execute(f"SELECT COUNT(*) FROM {target}").fetchone()[0]
        conn.execute(f"DELETE FROM {target}")
        conn.commit()

    print(f"✓  Rolled back '{target}': {before} rows deleted.")
    print(f"   Schema preserved — table is empty and ready for re-migration.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Rollback a target table")
    parser.add_argument("--target", required=True, choices=VALID_TABLES)
    parser.add_argument("--db", default="pipeline.db")
    args = parser.parse_args()
    rollback(args.target, args.db)
