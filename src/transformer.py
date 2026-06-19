"""
transformer.py — Stage 3: Transform
Applies schema mapping: normalizes strings, coerces types,
standardizes date formats, and maps legacy field names
to target schema column names.
"""

from datetime import datetime


# ── Legacy field name → target column mapping ─────────────
FIELD_MAP = {
    "ar_records": {
        "invoice_id":    "invoice_id",
        "customer_name": "customer_name",
        "amount":        "amount",
        "currency":      "currency",
        "due_date":      "due_date",
        "status":        "status",
        "created_at":    "created_at",
    },
    "ap_records": {
        "bill_id":        "bill_id",
        "vendor_name":    "vendor_name",
        "amount":         "amount",
        "currency":       "currency",
        "due_date":       "due_date",
        "payment_status": "payment_status",
        "created_at":     "created_at",
    },
    "vendor_records": {
        "vendor_id":     "vendor_id",
        "vendor_name":   "vendor_name",
        "contact_email": "contact_email",
        "phone":         "phone",
        "payment_terms": "payment_terms",
        "currency":      "currency",
        "active":        "active",
    },
}


def _normalize_date(val: str) -> str:
    """Standardize all dates to YYYY-MM-DD."""
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y"):
        try:
            return datetime.strptime(val, fmt).strftime("%Y-%m-%d")
        except (ValueError, TypeError):
            continue
    return val


def _normalize_bool(val: str) -> int:
    """Convert true/false/yes/no/1/0 to SQLite integer (1/0)."""
    if isinstance(val, str):
        return 1 if val.strip().lower() in ("true", "yes", "1") else 0
    return int(bool(val))


def transform_records(records: list[dict], target: str) -> list[dict]:
    """
    Map legacy fields to target schema and normalize values.
    Returns list of transformed dicts ready for DB insertion.
    """
    mapping     = FIELD_MAP.get(target, {})
    date_fields = {"due_date", "created_at"}
    bool_fields = {"active"}
    amt_fields  = {"amount"}

    transformed = []
    for record in records:
        row = {}
        for src_field, tgt_col in mapping.items():
            val = record.get(src_field)

            if val is None:
                row[tgt_col] = None
                continue

            # Type coercions
            if tgt_col in amt_fields:
                row[tgt_col] = float(val)
            elif tgt_col in date_fields:
                row[tgt_col] = _normalize_date(str(val))
            elif tgt_col in bool_fields:
                row[tgt_col] = _normalize_bool(val)
            else:
                # String normalization: strip, title-case names
                row[tgt_col] = str(val).strip()

        transformed.append(row)

    return transformed
