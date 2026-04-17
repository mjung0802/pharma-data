"""
verify.py — Smoke test for all SQL analytics queries.

Reads each .sql file in this directory, splits on '-- QUERY:' markers,
runs every query via run_query(), and confirms each returns at least one row.

Usage:
    python src/sql/verify.py
"""

import os
import sys
import textwrap

# Allow imports from the project root regardless of cwd.
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)

from src.ingestion.db import run_query  # noqa: E402

SQL_DIR = os.path.dirname(os.path.abspath(__file__))

SQL_FILES = [
    "claims_utilization.sql",
    "drug_cost.sql",
    "formulary_compliance.sql",
]


def parse_queries(sql_text: str) -> list[tuple[str, str]]:
    """
    Split *sql_text* on '-- QUERY: <name>' markers.

    Returns a list of (name, sql) tuples. Lines that precede the first
    marker (file-level comments) are silently dropped.
    """
    queries: list[tuple[str, str]] = []
    current_name: str | None = None
    current_lines: list[str] = []

    for line in sql_text.splitlines():
        stripped = line.strip()
        if stripped.startswith("-- QUERY:"):
            # Save previous block if any
            if current_name is not None:
                queries.append((current_name, "\n".join(current_lines).strip()))
            current_name = stripped[len("-- QUERY:"):].strip()
            current_lines = []
        else:
            if current_name is not None:
                current_lines.append(line)

    # Flush the last block
    if current_name is not None and current_lines:
        queries.append((current_name, "\n".join(current_lines).strip()))

    return queries


def verify_file(filename: str) -> int:
    """
    Parse and run all queries in *filename*.

    Prints results and returns the number of failed queries.
    """
    filepath = os.path.join(SQL_DIR, filename)
    print(f"\n{'=' * 70}")
    print(f"FILE: {filename}")
    print("=" * 70)

    with open(filepath, "r", encoding="utf-8") as fh:
        sql_text = fh.read()

    queries = parse_queries(sql_text)
    if not queries:
        print("  WARNING: no '-- QUERY:' markers found.")
        return 1

    failures = 0
    for name, sql in queries:
        print(f"\n  -- QUERY: {name}")
        try:
            df = run_query(sql)
            row_count = len(df)
            if row_count == 0:
                print(f"  FAIL  — query returned 0 rows")
                failures += 1
            else:
                print(f"  PASS  — {row_count} row(s) returned")
                # Show the first 5 rows, truncated to 120 chars per line
                preview = df.head(5).to_string(index=False)
                for line in preview.splitlines():
                    print("    " + line[:120])
        except Exception as exc:
            print(f"  FAIL  — exception: {exc}")
            failures += 1

    return failures


def main() -> None:
    total_failures = 0
    for filename in SQL_FILES:
        total_failures += verify_file(filename)

    print(f"\n{'=' * 70}")
    if total_failures == 0:
        print("ALL QUERIES PASSED.")
    else:
        print(f"{total_failures} QUERY/QUERIES FAILED — see output above.")
        sys.exit(1)


if __name__ == "__main__":
    main()
