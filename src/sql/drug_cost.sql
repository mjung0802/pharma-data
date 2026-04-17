-- =============================================================================
-- drug_cost.sql
-- Pillar 2: Brand vs. generic spend, top-cost drugs, therapeutic class breakdown
--
-- Runs against the `claims` table (DuckDB view of claims.csv).
-- Standard SQL compatible with BigQuery and DuckDB.
-- =============================================================================


-- QUERY: brand_vs_generic
-- Cost and claim volume split by drug type, with each type's share of total spend.
-- Filtered to Paid claims only to avoid inflating cost figures with Rejected/Reversed amounts.
SELECT
    drug_type,
    COUNT(*)                                                             AS claim_count,
    ROUND(SUM(gross_cost), 2)                                           AS total_gross_cost,
    ROUND(AVG(gross_cost), 2)                                           AS avg_gross_cost,
    ROUND(
        SUM(gross_cost) * 100.0
        / SUM(SUM(gross_cost)) OVER (),
        2
    )                                                                    AS pct_of_total_cost
FROM claims
WHERE claim_status = 'Paid'
GROUP BY drug_type
ORDER BY total_gross_cost DESC;


-- QUERY: top_10_drugs
-- Highest-spend individual drugs (Paid claims only), ranked by gross cost.
SELECT
    brand_name,
    generic_name,
    drug_type,
    therapeutic_class,
    COUNT(*)                                                             AS claim_count,
    ROUND(SUM(gross_cost), 2)                                           AS total_gross_cost,
    ROUND(SUM(total_paid), 2)                                           AS total_paid_amount
FROM claims
WHERE claim_status = 'Paid'
GROUP BY brand_name, generic_name, drug_type, therapeutic_class
ORDER BY total_gross_cost DESC
LIMIT 10;


-- QUERY: therapeutic_class_spend
-- Spend by therapeutic class with brand/generic cost split (Paid claims only).
SELECT
    therapeutic_class,
    COUNT(*)                                                             AS claim_count,
    ROUND(SUM(gross_cost), 2)                                           AS total_gross_cost,
    ROUND(AVG(gross_cost), 2)                                           AS avg_gross_cost,
    ROUND(SUM(CASE WHEN drug_type = 'Brand'   THEN gross_cost ELSE 0 END), 2) AS brand_cost,
    ROUND(SUM(CASE WHEN drug_type = 'Generic' THEN gross_cost ELSE 0 END), 2) AS generic_cost
FROM claims
WHERE claim_status = 'Paid'
GROUP BY therapeutic_class
ORDER BY total_gross_cost DESC;
