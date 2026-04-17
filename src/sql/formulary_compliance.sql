-- =============================================================================
-- formulary_compliance.sql
-- Pillar 3: Formulary tier adherence, generic fill rate, and on-formulary rate
--
-- Runs against the `claims` table (DuckDB view of claims.csv).
-- Standard SQL compatible with BigQuery and DuckDB.
--
-- Formulary tier definitions:
--   Tier 1 = preferred generics   (on formulary)
--   Tier 2 = preferred brands     (on formulary)
--   Tier 3 = non-preferred brands (off formulary)
-- =============================================================================


-- QUERY: tier_distribution
-- Claim volume and cost statistics per formulary tier (Paid claims only).
SELECT
    formulary_tier,
    COUNT(*)                                                             AS claim_count,
    ROUND(SUM(gross_cost), 2)                                           AS total_gross_cost,
    ROUND(AVG(gross_cost), 2)                                           AS avg_gross_cost,
    ROUND(AVG(member_copay), 2)                                         AS avg_member_copay
FROM claims
WHERE claim_status = 'Paid'
GROUP BY formulary_tier
ORDER BY formulary_tier ASC;


-- QUERY: generic_fill_rate
-- Overall brand vs. generic claim counts and generic fill rate (Paid claims only).
SELECT
    COUNT(*)                                                             AS total_claims,
    SUM(CASE WHEN drug_type = 'Generic' THEN 1 ELSE 0 END)             AS generic_claims,
    SUM(CASE WHEN drug_type = 'Brand'   THEN 1 ELSE 0 END)             AS brand_claims,
    ROUND(
        SUM(CASE WHEN drug_type = 'Generic' THEN 1 ELSE 0 END) * 100.0
        / COUNT(*),
        2
    )                                                                    AS generic_fill_rate
FROM claims
WHERE claim_status = 'Paid';


-- QUERY: on_formulary_rate
-- Proportion of Paid claims that landed on a preferred (Tier 1 or 2) formulary tier.
SELECT
    COUNT(*)                                                             AS total_paid_claims,
    SUM(CASE WHEN formulary_tier IN (1, 2) THEN 1 ELSE 0 END)          AS on_formulary_claims,
    SUM(CASE WHEN formulary_tier = 3       THEN 1 ELSE 0 END)          AS off_formulary_claims,
    ROUND(
        SUM(CASE WHEN formulary_tier IN (1, 2) THEN 1 ELSE 0 END) * 100.0
        / COUNT(*),
        2
    )                                                                    AS on_formulary_rate
FROM claims
WHERE claim_status = 'Paid';


-- QUERY: cost_per_tier
-- Claim volume and cost by formulary tier AND drug type (Paid claims only).
SELECT
    formulary_tier,
    drug_type,
    COUNT(*)                                                             AS claim_count,
    ROUND(SUM(gross_cost), 2)                                           AS total_gross_cost,
    ROUND(AVG(member_copay), 2)                                         AS avg_member_copay
FROM claims
WHERE claim_status = 'Paid'
GROUP BY formulary_tier, drug_type
ORDER BY formulary_tier ASC, drug_type ASC;
