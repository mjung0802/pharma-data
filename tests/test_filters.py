"""Unit tests for dashboard filter logic."""

import pytest
from werkzeug.datastructures import ImmutableMultiDict
from src.dashboard.routes._filters import (
    VALID_DRUG_TYPES,
    VALID_PLANS,
    _build_where,
    _inject_filter,
    get_filter_params,
    _mom_delta,
)

VALID_PLAN = next(iter(VALID_PLANS))
VALID_DRUG = next(iter(VALID_DRUG_TYPES))


class TestBuildWhere:
    def test_no_filters_returns_empty(self):
        assert _build_where("", "", "", "") == ""

    def test_valid_plan_included(self):
        result = _build_where(VALID_PLAN, "", "", "")
        assert f"plan_name = '{VALID_PLAN}'" in result

    def test_invalid_plan_ignored(self):
        result = _build_where("'; DROP TABLE claims;--", "", "", "")
        assert result == ""

    def test_plan_not_in_allowlist_ignored(self):
        result = _build_where("UnknownPlan", "", "", "")
        assert result == ""

    def test_valid_date_from_included(self):
        result = _build_where("", "2024-01-01", "", "")
        assert "service_date >= '2024-01-01'" in result

    def test_valid_date_to_included(self):
        result = _build_where("", "", "2024-12-31", "")
        assert "service_date <= '2024-12-31'" in result

    def test_invalid_date_format_ignored(self):
        assert _build_where("", "01/01/2024", "", "") == ""
        assert _build_where("", "", "12-31-2024", "") == ""

    def test_valid_drug_type_included(self):
        result = _build_where("", "", "", VALID_DRUG)
        assert f"drug_type = '{VALID_DRUG}'" in result

    def test_invalid_drug_type_ignored(self):
        result = _build_where("", "", "", "'; DROP TABLE--")
        assert result == ""

    def test_multiple_filters_combined(self):
        result = _build_where(VALID_PLAN, "2024-01-01", "2024-12-31", VALID_DRUG)
        assert result.startswith(" AND ")
        assert "plan_name" in result
        assert "service_date >=" in result
        assert "service_date <=" in result
        assert "drug_type" in result

    def test_result_starts_with_and(self):
        result = _build_where(VALID_PLAN, "", "", "")
        assert result.startswith(" AND ")


class TestInjectFilter:
    def test_empty_extra_where_unchanged(self):
        sql = "SELECT * FROM claims WHERE claim_status = 'Paid'"
        assert _inject_filter(sql, "") == sql

    def test_injects_subquery_around_claims(self):
        sql = "SELECT * FROM claims"
        result = _inject_filter(sql, " AND plan_name = 'X'")
        assert "_claims_filtered" in result
        assert "plan_name = 'X'" in result
        assert "WHERE 1=1" in result

    def test_case_insensitive_from_claims(self):
        sql = "SELECT * FROM CLAIMS"
        result = _inject_filter(sql, " AND drug_type = 'Generic'")
        assert "_claims_filtered" in result

    def test_multiple_from_claims_all_replaced(self):
        sql = "SELECT * FROM claims UNION ALL SELECT * FROM claims"
        result = _inject_filter(sql, " AND plan_name = 'X'")
        assert result.count("_claims_filtered") == 2

    def test_sql_without_from_claims_unchanged(self):
        sql = "SELECT 1 AS val"
        result = _inject_filter(sql, " AND plan_name = 'X'")
        assert result == sql


class TestGetFilterParams:
    def test_get_filter_params_all_fields(self):
        args = ImmutableMultiDict([
            ("plan", "AZ BlueCross PPO"),
            ("date_from", "2024-01-01"),
            ("date_to", "2024-12-31"),
            ("drug_type", "Generic"),
        ])
        assert get_filter_params(args) == {
            "plan_filter": "AZ BlueCross PPO",
            "date_from": "2024-01-01",
            "date_to": "2024-12-31",
            "drug_type": "Generic",
        }

    def test_get_filter_params_defaults_to_empty(self):
        assert get_filter_params(ImmutableMultiDict()) == {
            "plan_filter": "", "date_from": "", "date_to": "", "drug_type": ""
        }

    def test_get_filter_params_partial_fields(self):
        args = ImmutableMultiDict([
            ("plan", "Cigna Connect EPO"),
            ("date_from", "2024-06-01"),
        ])
        assert get_filter_params(args) == {
            "plan_filter": "Cigna Connect EPO",
            "date_from": "2024-06-01",
            "date_to": "",
            "drug_type": "",
        }

    def test_get_filter_params_with_dict(self):
        """Test that it works with regular dict-like objects."""
        args = {"plan": "UnitedHealth Select HMO", "date_from": "2024-03-15"}
        assert get_filter_params(args) == {
            "plan_filter": "UnitedHealth Select HMO",
            "date_from": "2024-03-15",
            "date_to": "",
            "drug_type": "",
        }



class TestMomDelta:
    def test_mom_delta_increase(self):
        delta, direction = _mom_delta([100, 120])
        assert delta == 20.0
        assert direction == "up"

    def test_mom_delta_decrease(self):
        delta, direction = _mom_delta([120, 60])
        assert delta == 50.0
        assert direction == "down"

    def test_mom_delta_insufficient_data(self):
        assert _mom_delta([100]) == (None, None)
        assert _mom_delta([]) == (None, None)

    def test_mom_delta_zero_prev(self):
        assert _mom_delta([0, 5]) == (None, None)
