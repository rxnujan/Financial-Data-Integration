"""
reconciler.py — Post-load reconciliation
Cross-checks source count vs loaded count and prints
a structured summary. Returns pass/fail status.
"""


def reconcile(source_count: int, valid_count: int,
              error_count: int, loaded_count: int) -> list[str]:
    lines = []
    lines.append(f"Source records   : {source_count}")
    lines.append(f"Valid records     : {valid_count}")
    lines.append(f"Errors / skipped  : {error_count}")
    lines.append(f"Loaded to DB      : {loaded_count}")
    lines.append("-" * 36)

    if loaded_count == valid_count and error_count == 0:
        lines.append("STATUS : ✓ PASS — All records migrated cleanly")
    elif loaded_count == valid_count and error_count > 0:
        lines.append(f"STATUS : ⚠ PARTIAL — {error_count} record(s) rejected (see error log)")
    else:
        lines.append(f"STATUS : ✗ FAIL — Loaded {loaded_count} but expected {valid_count}")

    return lines
