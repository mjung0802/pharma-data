"""
DuckDB engine and query interface.

``run_query(sql)`` is the **single interface** that all reports and dashboards
use to fetch data. It never exposes the underlying loader or the DuckDB
connection — callers only deal with plain DataFrames.

Switching from CSV to BigQuery requires only changing the PHARMA_DATA_SOURCE
environment variable; no report or dashboard code needs to change.
"""

import re
import duckdb
import pandas as pd

from src import config
from src.ingestion.base import TABLES


def get_engine() -> duckdb.DuckDBPyConnection:
    """
    Build and return a fresh in-memory DuckDB connection.

    Steps:
      1. Read ``config.DATA_SOURCE`` to choose the right loader.
      2. Load all five tables via the loader.
      3. Register each DataFrame as a DuckDB view so SQL can reference it by
         the canonical table name.

    Returns
    -------
    duckdb.DuckDBPyConnection
        An in-memory connection with views: claims, members, drugs, plans,
        pharmacies.

    Raises
    ------
    ValueError
        If ``config.DATA_SOURCE`` is not ``"csv"`` or ``"bigquery"``.
    """
    source = config.DATA_SOURCE.lower()

    if source == "csv":
        from src.ingestion.csv_loader import CSVLoader
        loader = CSVLoader()
    elif source == "bigquery":
        from src.ingestion.bigquery_loader import BigQueryLoader
        loader = BigQueryLoader()
    else:
        raise ValueError(
            f"Unsupported DATA_SOURCE '{source}'. "
            "Set PHARMA_DATA_SOURCE to 'csv' or 'bigquery'."
        )

    conn = duckdb.connect(database=":memory:")

    for table_name in TABLES:
        df: pd.DataFrame = loader.load(table_name)
        # Register the DataFrame as a view — DuckDB can query it by name
        conn.register(table_name, df)

    return conn


def run_query(sql: str) -> pd.DataFrame:
    """
    Execute *sql* against the current data source and return a DataFrame.

    This is the **only** function that reports and dashboards should call.
    A fresh engine (and therefore fresh data) is created on every call,
    which keeps the design simple and stateless — acceptable for a portfolio
    project that doesn't need caching.

    Parameters
    ----------
    sql:
        Any SQL statement that DuckDB can execute. Table names must match
        the canonical names: claims, members, drugs, plans, pharmacies.

    Returns
    -------
    pd.DataFrame
        Query results. Empty DataFrame if the query returns no rows.

    Example
    -------
    >>> from src.ingestion.db import run_query
    >>> df = run_query("SELECT COUNT(*) AS n FROM claims")
    >>> print(df)
         n
    0  800
    """
    conn = get_engine()
    try:
        return conn.execute(sql).df()
    finally:
        conn.close()


def _apply_dialect(sql: str, source: str = "duckdb") -> str:
    """Transform DuckDB SQL to BigQuery dialect, or return unchanged for DuckDB.

    Handles the two known dialect differences in this codebase:
      STRFTIME('%Y-%m', expr)         → FORMAT_DATE('%Y-%m', expr)
      DATEDIFF('day', date1, date2)   → DATE_DIFF(date2, date1, DAY)
    """
    if source != "bigquery":
        return sql
    sql = re.sub(r"\bSTRFTIME\s*\(", "FORMAT_DATE(", sql, flags=re.IGNORECASE)
    sql = re.sub(
        r"\bDATEDIFF\s*\(\s*'day'\s*,\s*([^,]+),\s*([^)]+)\)",
        r"DATE_DIFF(\2, \1, DAY)",
        sql,
        flags=re.IGNORECASE,
    )
    return sql


# ---------------------------------------------------------------------------
# Inline smoke test — run this file directly to verify the data layer works.
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    print("Running smoke test: SELECT COUNT(*) AS n FROM claims")
    result = run_query("SELECT COUNT(*) AS n FROM claims")
    print(result)

    expected = 800
    actual = int(result["n"].iloc[0])
    if actual == expected:
        print(f"\nPASSED — claims row count is {actual} as expected.")
    else:
        print(f"\nFAILED — expected {expected} rows, got {actual}.")

    # Quick sanity checks on the other tables
    print("\nRow counts across all tables:")
    for table in ("claims", "members", "drugs", "plans", "pharmacies"):
        count_df = run_query(f"SELECT COUNT(*) AS n FROM {table}")
        n = int(count_df["n"].iloc[0])
        print(f"  {table:<15} {n:>5} rows")
