#!/usr/bin/env python3
"""
pipeline.py — Financial Data Integration & Validation Suite
============================================================
Usage:
  python pipeline.py --input sample_data/ar_records.csv  --target ar_records
  python pipeline.py --input sample_data/ap_records.csv  --target ap_records
  python pipeline.py --input sample_data/vendor_records.csv --target vendor_records
"""

import argparse
import sys
from src.extractor   import extract_csv
from src.validator   import validate_records
from src.transformer import transform_records
from src.loader      import init_db, load_records, log_migration
from src.reconciler  import reconcile
from src.logger      import PipelineLogger


def run_pipeline(input_file: str, target: str, db_path: str = "pipeline.db") -> int:
    logger = PipelineLogger(target)

    print(f"\n{'='*58}")
    print(f"  Financial Data Integration Pipeline  v1.0")
    print(f"  Target : {target}")
    print(f"  Source : {input_file}")
    print(f"  Run ID : {logger.run_id}")
    print(f"{'='*58}\n")

    # ── Stage 1: Extract ──────────────────────────────────
    print("[1/4]  EXTRACTING ...")
    records, source_count = extract_csv(input_file)
    print(f"       ✓  {source_count} records extracted\n")

    # ── Stage 2: Validate ─────────────────────────────────
    print("[2/4]  VALIDATING ...")
    valid_records, errors = validate_records(records, target)
    for err in errors:
        logger.log_error(err)
    print(f"       ✓  Valid: {len(valid_records)}  |  Rejected: {len(errors)}\n")

    if not valid_records:
        print("  [ABORT] No valid records to load.\n")
        sys.exit(1)

    # ── Stage 3: Transform ────────────────────────────────
    print("[3/4]  TRANSFORMING ...")
    transformed = transform_records(valid_records, target)
    print(f"       ✓  {len(transformed)} records transformed\n")

    # ── Stage 4: Load ─────────────────────────────────────
    print("[4/4]  LOADING ...")
    init_db(db_path)
    loaded_count = load_records(transformed, target, db_path)
    print(f"       ✓  {loaded_count} records loaded into '{target}'\n")

    # ── Reconciliation ────────────────────────────────────
    print("  RECONCILIATION REPORT")
    print("  " + "-"*36)
    for line in reconcile(source_count, len(valid_records), len(errors), loaded_count):
        print(f"  {line}")

    # ── Audit log ─────────────────────────────────────────
    status = "PASS" if loaded_count == len(valid_records) else "PARTIAL"
    log_migration(
        logger.run_id, target, input_file,
        source_count, len(valid_records), len(errors), loaded_count,
        status, db_path
    )
    log_file = logger.save()
    print(f"\n  Error log : {log_file}")
    print(f"  DB path   : {db_path}")
    print(f"\n{'='*58}\n")

    return loaded_count


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Financial Data Integration & Validation Pipeline"
    )
    parser.add_argument("--input",  required=True,
                        help="Path to source CSV file")
    parser.add_argument("--target", required=True,
                        choices=["ar_records", "ap_records", "vendor_records"],
                        help="Target table name")
    parser.add_argument("--db",     default="pipeline.db",
                        help="SQLite DB path (default: pipeline.db)")
    args = parser.parse_args()
    run_pipeline(args.input, args.target, args.db)
