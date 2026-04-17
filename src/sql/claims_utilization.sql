-- =============================================================================
-- claims_utilization.sql
-- Pillar 1: Claims volume, status mix, monthly trends, and plan-level breakdown
--
-- Runs against the `claims` table (DuckDB view of claims.csv).
-- Standard SQL compatible with BigQuery and DuckDB.
-- =============================================================================


-- QUERY: status_summary
-- Count and total_paid per claim_status, plus the overall paid_rate
-- (Paid count / total count * 100) as a global figure on every row.
--
-- paid_rate is computed via a correlated subquery so it is identical on
-- every row — useful for downstream pivot tables and dashboard KPI cards.
-- Both DuckDB and BigQuery support scalar subqueries in SELECT.
WITH status_counts AS (
    SELECT
        claim_status,
        COUNT(*)                AS claim_count,
        ROUND(SUM(total_paid), 2) AS total_paid
    FROM claims
    GROUP BY claim_status
)
SELECT
    sc.claim_status,
    sc.claim_count,
    sc.total_paid,
    ROUND(
        (SELECT SUM(claim_count) FROM status_counts WHERE claim_status = 'Paid')
        * 100.0
        / (SELECT SUM(claim_count) FROM status_counts),
        2
    )                                                                    AS paid_rate
FROM status_counts sc
ORDER BY sc.claim_count DESC;


-- QUERY: monthly_trend
-- Month-over-month claim volume, gross cost, and paid amount.
-- DuckDB:     STRFTIME('%Y-%m', CAST(service_date AS DATE))
-- BigQuery:   FORMAT_DATE('%Y-%m', CAST(service_date AS DATE))
SELECT
    STRFTIME('%Y-%m', CAST(service_date AS DATE))                        AS year_month,
    COUNT(*)                                                             AS claim_count,
    ROUND(SUM(gross_cost), 2)                                           AS total_gross_cost,
    ROUND(SUM(total_paid), 2)                                           AS total_paid,
    SUM(CASE WHEN claim_status = 'Paid' THEN 1 ELSE 0 END)             AS paid_count
FROM claims
GROUP BY STRFTIME('%Y-%m', CAST(service_date AS DATE))
ORDER BY year_month ASC;


-- QUERY: plan_breakdown
-- Per-plan claim counts by status, cost totals, and paid rate.
SELECT
    plan_name,
    COUNT(*)                                                             AS claim_count,
    SUM(CASE WHEN claim_status = 'Paid'     THEN 1 ELSE 0 END)         AS paid_count,
    SUM(CASE WHEN claim_status = 'Rejected' THEN 1 ELSE 0 END)         AS rejected_count,
    SUM(CASE WHEN claim_status = 'Reversed' THEN 1 ELSE 0 END)         AS reversed_count,
    ROUND(SUM(gross_cost), 2)                                           AS total_gross_cost,
    ROUND(SUM(plan_paid), 2)                                            AS total_plan_paid,
    ROUND(
        SUM(CASE WHEN claim_status = 'Paid' THEN 1 ELSE 0 END) * 100.0
        / COUNT(*),
        2
    )                                                                    AS paid_rate
FROM claims
GROUP BY plan_name
ORDER BY claim_count DESC;
