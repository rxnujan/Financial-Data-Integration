-- ============================================================
-- Financial Data Integration Suite — Schema Definitions
-- Compatible with SQLite (demo) and PostgreSQL (production)
-- ============================================================

-- Accounts Receivable
CREATE TABLE IF NOT EXISTS ar_records (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    invoice_id  TEXT    NOT NULL UNIQUE,
    customer_name TEXT  NOT NULL,
    amount      REAL    NOT NULL CHECK(amount > 0),
    currency    TEXT    NOT NULL DEFAULT 'INR',
    due_date    TEXT    NOT NULL,
    status      TEXT    NOT NULL CHECK(status IN ('pending','paid','overdue')),
    created_at  TEXT    NOT NULL,
    loaded_at   TEXT    NOT NULL DEFAULT (datetime('now'))
);

-- Accounts Payable
CREATE TABLE IF NOT EXISTS ap_records (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    bill_id        TEXT    NOT NULL UNIQUE,
    vendor_name    TEXT    NOT NULL,
    amount         REAL    NOT NULL CHECK(amount > 0),
    currency       TEXT    NOT NULL DEFAULT 'INR',
    due_date       TEXT    NOT NULL,
    payment_status TEXT    NOT NULL CHECK(payment_status IN ('pending','paid','overdue')),
    created_at     TEXT    NOT NULL,
    loaded_at      TEXT    NOT NULL DEFAULT (datetime('now'))
);

-- Vendor Master
CREATE TABLE IF NOT EXISTS vendor_records (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    vendor_id     TEXT    NOT NULL UNIQUE,
    vendor_name   TEXT    NOT NULL,
    contact_email TEXT,
    phone         TEXT,
    payment_terms TEXT    NOT NULL DEFAULT 'NET30',
    currency      TEXT    NOT NULL DEFAULT 'INR',
    active        INTEGER NOT NULL DEFAULT 1,
    loaded_at     TEXT    NOT NULL DEFAULT (datetime('now'))
);

-- Migration audit log
CREATE TABLE IF NOT EXISTS migration_log (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id      TEXT    NOT NULL,
    target      TEXT    NOT NULL,
    source_file TEXT    NOT NULL,
    source_count  INTEGER,
    valid_count   INTEGER,
    error_count   INTEGER,
    loaded_count  INTEGER,
    status      TEXT,
    run_at      TEXT    NOT NULL DEFAULT (datetime('now'))
);
