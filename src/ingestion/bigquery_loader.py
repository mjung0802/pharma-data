"""
BigQuery data loader.

Requirements:  pip install google-cloud-bigquery db-dtypes
Configuration: GCP_PROJECT and GCP_DATASET environment variables.
Authentication: gcloud auth application-default login
"""
from __future__ import annotations

import pandas as pd

from src import config
from src.ingestion.base import DataLoader, TABLES

try:
    from google.cloud import bigquery as _bq
    import db_dtypes as _db_dtypes  # noqa: F401 — ensures BQ datetime types deserialise
    _HAS_BQ = True
except ImportError:
    _HAS_BQ = False


class BigQueryLoader(DataLoader):
    """Load tables from BigQuery into DataFrames for DuckDB in-memory analysis."""

    def load(self, table_name: str) -> pd.DataFrame:
        if not _HAS_BQ:
            raise ImportError(
                "BigQueryLoader requires google-cloud-bigquery and db-dtypes. "
                "Install: pip install google-cloud-bigquery db-dtypes"
            )
        if table_name not in TABLES:
            raise ValueError(
                f"Unknown table: {table_name!r}. Valid tables: {sorted(TABLES)}"
            )
        client = _bq.Client(project=config.GCP_PROJECT)
        query = (
            f"SELECT * FROM "
            f"`{config.GCP_PROJECT}.{config.GCP_DATASET}.{table_name}`"
        )
        return client.query(query).to_dataframe()
