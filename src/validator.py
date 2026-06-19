"""
validator.py — Stage 2: Validate
Enforces field-level rules: required fields, type checks,
value ranges, allowed values, and duplicate detection.
Returns (valid_records, error_list).
"""

from datetime import datetime


# ── Validation rule definitions per target table ─────────
RULES = {
    "ar_records": {
        "required":      ["invoice_id", "customer_name", "amount", "currency", "due_date", "status", "created_at"],
        "unique_key":    "invoice_id",
        "positive_amt":  "amount",
        "allowed": {
            "status":   ["pending", "paid", "overdue"],
            "currency": ["INR", "USD", "EUR", "GBP"],
        },
        "date_fields":   ["due_date", "created_at"],
    },
    "ap_records": {
        "required":      ["bill_id", "vendor_name", "amount", "currency", "due_date", "payment_status", "created_at"],
        "unique_key":    "bill_id",
        "positive_amt":  "amount",
        "allowed": {
            "payment_status": ["pending", "paid", "overdue"],
            "currency":       ["INR", "USD", "EUR", "GBP"],
        },
        "date_fields":   ["due_date", "created_at"],
    },
    "vendor_records": {
        "required":      ["vendor_id", "vendor_name", "payment_terms", "currency"],
        "unique_key":    "vendor_id",
        "allowed": {
            "payment_terms": ["NET15", "NET30", "NET45", "NET60"],
            "currency":      ["INR", "USD", "EUR", "GBP"],
        },
        "date_fields":   [],
    },
}


def _is_valid_date(val: str) -> bool:
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y"):
        try:
            datetime.strptime(val, fmt)
            return True
        except ValueError:
            continue
    return False


def validate_records(records: list[dict], target: str) -> tuple[list[dict], list[dict]]:
    """
    Validate each record against the rules for `target`.
    Returns (valid_records, errors).
    Each error is a dict: {row, field, issue, value}.
    """
    rules = RULES.get(target, {})
    required      = rules.get("required", [])
    unique_key    = rules.get("unique_key")
    positive_amt  = rules.get("positive_amt")
    allowed       = rules.get("allowed", {})
    date_fields   = rules.get("date_fields", [])

    valid_records = []
    errors        = []
    seen_keys     = set()

    for i, record in enumerate(records, start=1):
        row_errors = []

        # 1. Required field check (null / missing)
        for field in required:
            if record.get(field) is None or str(record.get(field, "")).strip() == "":
                row_errors.append({
                    "row": i, "field": field,
                    "issue": "MISSING_REQUIRED_FIELD",
                    "value": None,
                })

        # 2. Duplicate key check
        if unique_key:
            key_val = record.get(unique_key)
            if key_val in seen_keys:
                row_errors.append({
                    "row": i, "field": unique_key,
                    "issue": "DUPLICATE_KEY",
                    "value": key_val,
                })
            else:
                seen_keys.add(key_val)

        # 3. Positive amount check
        if positive_amt and record.get(positive_amt) is not None:
            try:
                amt = float(record[positive_amt])
                if amt <= 0:
                    row_errors.append({
                        "row": i, "field": positive_amt,
                        "issue": "NEGATIVE_OR_ZERO_AMOUNT",
                        "value": record[positive_amt],
                    })
            except (ValueError, TypeError):
                row_errors.append({
                    "row": i, "field": positive_amt,
                    "issue": "INVALID_AMOUNT_FORMAT",
                    "value": record[positive_amt],
                })

        # 4. Allowed values check
        for field, allowed_vals in allowed.items():
            val = record.get(field)
            if val is not None and val not in allowed_vals:
                row_errors.append({
                    "row": i, "field": field,
                    "issue": "INVALID_VALUE",
                    "value": val,
                })

        # 5. Date format check
        for field in date_fields:
            val = record.get(field)
            if val is not None and not _is_valid_date(val):
                row_errors.append({
                    "row": i, "field": field,
                    "issue": "INVALID_DATE_FORMAT",
                    "value": val,
                })

        if row_errors:
            errors.extend(row_errors)
        else:
            valid_records.append(record)

    return valid_records, errors
