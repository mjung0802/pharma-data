"""Tests for dashboard route empty-result handling."""

import pandas as pd
import pytest
from unittest.mock import patch


@pytest.fixture
def client():
    from src.dashboard.app import create_app
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


def _claims_dfs():
    """Empty DataFrames matching the schema of each claims SQL query."""
    return [
        pd.DataFrame(columns=["claim_status", "claim_count", "total_paid", "paid_rate"]),
        pd.DataFrame(columns=["year_month", "claim_count", "total_gross_cost", "total_paid", "paid_count"]),
        pd.DataFrame(columns=["plan_name", "paid_count", "rejected_count", "reversed_count"]),
    ]


def _drugs_dfs():
    return [
        pd.DataFrame(columns=["drug_type", "total_gross_cost"]),
        pd.DataFrame(columns=["brand_name", "total_gross_cost"]),
        pd.DataFrame(columns=["therapeutic_class", "brand_cost", "generic_cost"]),
    ]


def _formulary_dfs():
    return [
        pd.DataFrame(columns=["formulary_tier", "total_gross_cost"]),
        pd.DataFrame(columns=["generic_fill_rate", "generic_claims", "brand_claims"]),
        pd.DataFrame(columns=["on_formulary_rate", "total_paid_claims"]),
        pd.DataFrame(columns=["drug_type", "formulary_tier", "avg_member_copay"]),
    ]


class TestClaimsEmptyResult:
    def test_returns_200_on_empty_data(self, client):
        with patch("src.ingestion.run_query", side_effect=_claims_dfs()):
            resp = client.get("/claims")
        assert resp.status_code == 200

    def test_returns_200_with_filter_params(self, client):
        with patch("src.ingestion.run_query", side_effect=_claims_dfs()):
            resp = client.get("/claims?plan=AZ+BlueCross+PPO&date_from=2024-01-01")
        assert resp.status_code == 200


class TestDrugsEmptyResult:
    def test_returns_200_on_empty_data(self, client):
        with patch("src.ingestion.run_query", side_effect=_drugs_dfs()):
            resp = client.get("/drugs")
        assert resp.status_code == 200


class TestFormularyEmptyResult:
    def test_returns_200_on_empty_data(self, client):
        with patch("src.ingestion.run_query", side_effect=_formulary_dfs()):
            resp = client.get("/formulary")
        assert resp.status_code == 200
