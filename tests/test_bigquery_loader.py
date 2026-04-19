import sys
import pytest
import pandas as pd
from unittest.mock import MagicMock, patch


def _install_mock_bq(monkeypatch):
    """Inject fake google.cloud.bigquery and db_dtypes into sys.modules."""
    mock_bq = MagicMock()
    mock_google = MagicMock()
    mock_google_cloud = MagicMock()
    mock_google_cloud.bigquery = mock_bq
    mock_google.cloud = mock_google_cloud

    monkeypatch.setitem(sys.modules, "google", mock_google)
    monkeypatch.setitem(sys.modules, "google.cloud", mock_google_cloud)
    monkeypatch.setitem(sys.modules, "google.cloud.bigquery", mock_bq)
    monkeypatch.setitem(sys.modules, "db_dtypes", MagicMock())
    return mock_bq


def test_bigquery_loader_load_returns_dataframe(monkeypatch):
    mock_bq = _install_mock_bq(monkeypatch)

    mock_df = pd.DataFrame({"a": [1, 2, 3]})
    mock_client = MagicMock()
    mock_client.query.return_value.to_dataframe.return_value = mock_df
    mock_bq.Client.return_value = mock_client

    monkeypatch.setenv("GCP_PROJECT", "my-project")
    monkeypatch.setenv("GCP_DATASET", "pharma")

    from importlib import reload
    import src.ingestion.bigquery_loader as m
    reload(m)
    loader = m.BigQueryLoader()
    result = loader.load("claims")

    assert isinstance(result, pd.DataFrame)
    query_arg = mock_client.query.call_args[0][0]
    assert "claims" in query_arg


def test_bigquery_loader_rejects_unknown_table(monkeypatch):
    mock_bq = _install_mock_bq(monkeypatch)
    mock_bq.Client.return_value = MagicMock()

    monkeypatch.setenv("GCP_PROJECT", "proj")
    monkeypatch.setenv("GCP_DATASET", "ds")

    from importlib import reload
    import src.ingestion.bigquery_loader as m
    reload(m)
    loader = m.BigQueryLoader()
    with pytest.raises(ValueError, match="Unknown table"):
        loader.load("unknown_table")


def test_bigquery_loader_raises_import_error_without_deps(monkeypatch):
    monkeypatch.setitem(sys.modules, "google.cloud.bigquery", None)
    monkeypatch.setitem(sys.modules, "db_dtypes", None)
    from importlib import reload
    import src.ingestion.bigquery_loader as m
    reload(m)
    loader = m.BigQueryLoader()
    with pytest.raises(ImportError, match="google-cloud-bigquery"):
        loader.load("claims")


def test_apply_dialect_duckdb_is_noop():
    from src.ingestion.db import _apply_dialect
    sql = "SELECT STRFTIME('%Y-%m', CAST(d AS DATE)) FROM t"
    assert _apply_dialect(sql, source="duckdb") == sql


def test_apply_dialect_bigquery_replaces_strftime():
    from src.ingestion.db import _apply_dialect
    sql = "SELECT STRFTIME('%Y-%m', CAST(d AS DATE)) FROM t"
    result = _apply_dialect(sql, source="bigquery")
    assert "FORMAT_DATE" in result
    assert "STRFTIME" not in result


def test_apply_dialect_bigquery_replaces_datediff():
    from src.ingestion.db import _apply_dialect
    sql = "SELECT DATEDIFF('day', CAST(a AS DATE), CAST(b AS DATE)) FROM t"
    result = _apply_dialect(sql, source="bigquery")
    assert "DATE_DIFF" in result
    assert "DATEDIFF" not in result
    # Verify argument order is swapped: DATE_DIFF(date2, date1, DAY)
    assert "DATE_DIFF(CAST(b AS DATE), CAST(a AS DATE), DAY)" in result
