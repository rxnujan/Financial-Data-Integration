-- ============================================================
-- Reconciliation & Validation Queries
-- Run these after each migration to verify data integrity
-- ============================================================

-- 1. Record count per table
SELECT 'ar_records'     AS table_name, COUNT(*) AS record_count FROM ar_records
UNION ALL
SELECT 'ap_records',    COUNT(*) FROM ap_records
UNION ALL
SELECT 'vendor_records',COUNT(*) FROM vendor_records;

-- 2. AR — total outstanding by currency
SELECT currency, SUM(amount) AS total_outstanding
FROM ar_records
WHERE status = 'pending'
GROUP BY currency;

-- 3. AP — overdue bills
SELECT bill_id, vendor_name, amount, due_date
FROM ap_records
WHERE payment_status = 'overdue'
ORDER BY due_date ASC;

-- 4. Duplicate check (should return 0 rows if clean)
SELECT invoice_id, COUNT(*) AS occurrences
FROM ar_records
GROUP BY invoice_id
HAVING COUNT(*) > 1;

-- 5. Migration audit — latest run summary
SELECT run_id, target, source_count, valid_count, error_count, loaded_count, status, run_at
FROM migration_log
ORDER BY run_at DESC
LIMIT 10;

-- 6. Data integrity: AR amounts in valid range
SELECT invoice_id, amount
FROM ar_records
WHERE amount <= 0 OR amount > 10000000;

-- 7. Vendors without contact info (data quality check)
SELECT vendor_id, vendor_name
FROM vendor_records
WHERE contact_email IS NULL OR phone IS NULL;
