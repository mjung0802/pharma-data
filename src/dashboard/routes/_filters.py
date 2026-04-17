"""
Shared filter helpers for all dashboard routes.

Provides allowlist constants and _build_where() for safe SQL WHERE clause
construction from user-supplied GET query parameters.
"""

from __future__ import annotations

import re

VALID_PLANS: frozenset[str] = frozenset(
    {
        "AZ BlueCross PPO",
        "UnitedHealth Select HMO",
        "Aetna Advantage POS",
        "Cigna Connect EPO",
    }
)

VALID_DRUG_TYPES: frozenset[str] = frozenset({"Brand", "Generic"})

_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def _build_where(plan: str, date_from: str, date_to: str, drug_type: str) -> str:
    """Return a safe WHERE clause fragment (including leading AND) or '' if none.

    All user-supplied values are validated against allowlists or a strict regex
    before being interpolated into SQL, preventing injection attacks.

    Args:
        plan:      Plan name, or empty string for "All Plans".
        date_from: Service-date lower bound in YYYY-MM-DD format, or empty.
        date_to:   Service-date upper bound in YYYY-MM-DD format, or empty.
        drug_type: "Brand", "Generic", or empty string for all types.

    Returns:
        A string that starts with " AND " followed by joined conditions,
        or an empty string when no filters are active.
    """
    conditions: list[str] = []

    if plan and plan in VALID_PLANS:
        conditions.append(f"plan_name = '{plan}'")

    if date_from and _DATE_RE.match(date_from):
        conditions.append(f"service_date >= '{date_from}'")

    if date_to and _DATE_RE.match(date_to):
        conditions.append(f"service_date <= '{date_to}'")

    if drug_type and drug_type in VALID_DRUG_TYPES:
        conditions.append(f"drug_type = '{drug_type}'")

    if not conditions:
        return ""

    return " AND " + " AND ".join(conditions)


def _inject_filter(sql: str, extra_where: str) -> str:
    """Inject *extra_where* into a SQL query string safely.

    Strategy: replace every ``FROM claims`` occurrence (case-insensitive, at a
    word boundary) with a subquery that wraps the table in a WHERE filter::

        FROM (SELECT * FROM claims WHERE 1=1 AND ...) AS _claims_filtered

    This approach is robust across simple queries, queries with existing WHERE
    clauses, CTE inner queries, and window-function FILTER clauses — none of
    which need special-casing.

    When *extra_where* is empty the original SQL is returned unchanged.
    """
    if not extra_where:
        return sql

    subquery = f"(SELECT * FROM claims WHERE 1=1{extra_where}) AS _claims_filtered"
    return re.sub(r"\bFROM\s+claims\b", f"FROM {subquery}", sql, flags=re.IGNORECASE)
