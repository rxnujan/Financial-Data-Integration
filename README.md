# Financial Data Integration & Validation Suite

A production-style ETL pipeline that extracts, validates, transforms, and loads structured financial records (AR, AP, Vendor) across system boundaries — with SQL reconciliation, structured error logging, and rollback support.

Built to mirror real-world integration consulting workflows: schema mapping, data integrity enforcement, and audit-trail generation.

---

## Features

- **4-stage pipeline**: Extract → Validate → Transform → Load
- **Field-level validation**: null checks, type enforcement, duplicate detection, value range, date format
- **Schema mapping**: translates legacy flat-file column structures to normalized relational tables
- **Idempotent loading**: `INSERT OR IGNORE` — safe to re-run without creating duplicates
- **SQL reconciliation**: cross-verifies source vs loaded record counts
- **Structured JSON error logs**: per-run, per-record error reports saved to `logs/`
- **Rollback utility**: clears a target table safely while preserving schema
- **Migration audit log**: every run is recorded with counts and status

---

## Tech Stack

`Python` · `Pandas` · `SQLite` (PostgreSQL-compatible) · `SQL` · `argparse` · `Linux/Bash`

---

## Project Structure

```
financial-data-integration-suite/
├── pipeline.py              # Main entry point
├── rollback.py              # Rollback utility
├── requirements.txt
├── sample_data/
│   ├── ar_records.csv       # Accounts Receivable sample
│   ├── ap_records.csv       # Accounts Payable sample
│   └── vendor_records.csv   # Vendor master sample
├── src/
│   ├── extractor.py         # Stage 1: CSV extraction
│   ├── validator.py         # Stage 2: Field-level validation
│   ├── transformer.py       # Stage 3: Schema mapping & type coercion
│   ├── loader.py            # Stage 4: SQLite bulk load + audit log
│   ├── reconciler.py        # Post-load reconciliation report
│   └── logger.py            # Structured JSON error logging
└── sql/
    ├── schema.sql            # Table definitions (SQLite + PostgreSQL)
    └── reconciliation_queries.sql  # Manual validation queries
```

---

## Quickstart

```bash
# 1. Clone and install
git clone https://github.com/YOUR_USERNAME/financial-data-integration-suite
cd financial-data-integration-suite
pip install -r requirements.txt

# 2. Run the pipeline
python pipeline.py --input sample_data/ar_records.csv --target ar_records
python pipeline.py --input sample_data/ap_records.csv --target ap_records
python pipeline.py --input sample_data/vendor_records.csv --target vendor_records

# 3. Rollback a table (if needed)
python rollback.py --target ar_records
```

---

## Sample Output

```
==========================================================
  Financial Data Integration Pipeline  v1.0
  Target : ar_records
  Source : sample_data/ar_records.csv
  Run ID : a3f1bc2d
==========================================================

[1/4]  EXTRACTING ...
       ✓  11 records extracted

[2/4]  VALIDATING ...
       ✗ Row 4  | customer_name | MISSING_REQUIRED_FIELD | value=None
       ✗ Row 8  | amount        | NEGATIVE_OR_ZERO_AMOUNT | value='-5000.00'
       ✗ Row 9  | invoice_id    | DUPLICATE_KEY | value='INV-002'
       ✓  Valid: 8  |  Rejected: 3

[3/4]  TRANSFORMING ...
       ✓  8 records transformed

[4/4]  LOADING ...
       ✓  8 records loaded into 'ar_records'

  RECONCILIATION REPORT
  ------------------------------------
  Source records   : 11
  Valid records    : 8
  Errors / skipped : 3
  Loaded to DB     : 8
  ------------------------------------
  STATUS : ⚠ PARTIAL — 3 record(s) rejected (see error log)

  Error log : logs/ar_records_a3f1bc2d.json
  DB path   : pipeline.db
==========================================================
```

---

## PostgreSQL (Production)

The schema in `sql/schema.sql` is PostgreSQL-compatible. To switch from SQLite:
1. Install `psycopg2`: `pip install psycopg2-binary`
2. Update the connection in `src/loader.py` to use `psycopg2.connect()`
3. Run `sql/schema.sql` against your PostgreSQL instance

---

## Author

Govindam Gourav Ramanujam — github.com/rxnujan
