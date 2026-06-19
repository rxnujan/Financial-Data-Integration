"""
extractor.py — Stage 1: Extract
Reads CSV source file into a list of records (dicts).
Returns raw records + source count for reconciliation.
"""

import pandas as pd
import sys


def extract_csv(filepath: str) -> tuple[list[dict], int]:
    """
    Read a CSV file and return (records, source_count).
    Strips whitespace from all string fields.
    """
    try:
        df = pd.read_csv(filepath, dtype=str)
    except FileNotFoundError:
        print(f"  [ERROR] File not found: {filepath}")
        sys.exit(1)
    except Exception as e:
        print(f"  [ERROR] Failed to read CSV: {e}")
        sys.exit(1)

    # Strip whitespace from all string columns
    df = df.map(lambda x: x.strip() if isinstance(x, str) else x)

    # Replace empty strings with None (treat as null)
    df = df.where(pd.notna(df), None)
    df = df.replace("", None)

    records = df.to_dict(orient="records")
    source_count = len(records)

    return records, source_count
