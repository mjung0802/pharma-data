"""
Basic test suite for the Phase 1 data layer.

Tests cover:
- CSVLoader loads all 5 tables without error and returns a non-empty DataFrame
- run_query returns correct row count for the claims table
- CSVLoader raises ValueError for an unknown table name
- CSVLoader raises ValueError for a path-traversal attempt (blocked by allowlist)
"""

import pytest
import pandas as pd

from src.ingestion.csv_loader import CSVLoader
from src.ingestion.db import run_query
from src.ingestion.base import TABLES


class TestCSVLoaderLoadsTables:
    """CSVLoader should load every canonical table as a non-empty DataFrame."""

    def setup_method(self):
        self.loader = CSVLoader()

    @pytest.mark.parametrize("table_name", TABLES)
    def test_load_returns_nonempty_dataframe(self, table_name):
        df = self.loader.load(table_name)
        assert isinstance(df, pd.DataFrame), (
            f"Expected DataFrame for table '{table_name}', got {type(df)}"
        )
        assert not df.empty, f"DataFrame for table '{table_name}' must not be empty"


class TestRunQuery:
    """run_query should execute SQL against the in-memory DuckDB engine."""

    def test_claims_row_count(self):
        df = run_query("SELECT COUNT(*) as n FROM claims")
        assert isinstance(df, pd.DataFrame)
        assert "n" in df.columns
        assert int(df["n"].iloc[0]) == 800


class TestCSVLoaderValidation:
    """CSVLoader should raise ValueError for invalid or unsafe table names."""

    def setup_method(self):
        self.loader = CSVLoader()

    def test_unknown_table_raises_value_error(self):
        with pytest.raises(ValueError, match="unknown_table"):
            self.loader.load("unknown_table")

    def test_path_traversal_raises_value_error(self):
        with pytest.raises(ValueError):
            self.loader.load("bad/../table")


class TestGeoData:
    """Members and pharmacies should span multiple US states."""

    def test_members_have_multiple_states(self):
        df = CSVLoader().load("members")
        states = df["state"].unique().tolist()
        assert len(states) > 1, f"Expected multiple states, got: {states}"

    def test_pharmacies_have_multiple_states(self):
        df = CSVLoader().load("pharmacies")
        state_col = [c for c in df.columns if "state" in c.lower()][0]
        states = df[state_col].unique().tolist()
        assert len(states) > 1, f"Expected multiple states, got: {states}"
