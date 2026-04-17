# GCP Migration Architecture

## 1. Overview

This document describes how the pharma claims analytics project is architected for cloud readiness. The system deliberately uses DuckDB as its local SQL engine because its dialect is fully compatible with BigQuery—this design choice enables a straightforward migration path: switching from local CSV files to cloud-hosted data requires only a configuration change, not a rewrite. The migration is a portfolio piece demonstrating cloud-native architecture planning and thoughtful abstraction layer design.

## 2. Current Architecture (Local)

```
data/*.csv  →  CSVLoader  →  DuckDB (in-memory)  →  Excel Reports
                                               →  Flask Dashboard
```

**Components:**

- **CSV Files** — Five data tables stored locally under `data/`: `claims.csv` (800 rows), `members.csv`, `drugs.csv`, `plans.csv`, `pharmacies.csv`. These are the source of truth during development.

- **CSVLoader** — The `src/ingestion/csv_loader.py` module implements the `DataLoader` interface. It reads each table from its corresponding CSV file and returns a pandas DataFrame. This is the default loader.

- **DuckDB** — An in-memory SQL engine (`src/ingestion/db.py`) that registers each loaded DataFrame as a view. All queries run against these DuckDB views. Fresh connections are instantiated per query, keeping the design stateless and simple.

- **Reports & Dashboard** — Excel reports (`src/reports/excel/`) and the Flask dashboard (`src/dashboard/`) both call `src.ingestion.db.run_query(sql)`, the single query interface. Neither layer knows which data source is active.

**Data Source Selection:**

```python
# In src/config.py
DATA_SOURCE = os.getenv("PHARMA_DATA_SOURCE", "csv")
```

Setting `PHARMA_DATA_SOURCE=csv` (the default) activates the CSVLoader. Setting `PHARMA_DATA_SOURCE=bigquery` would activate the BigQueryLoader (once implemented).

## 3. Target Architecture (Google Cloud)

```
Cloud Storage (raw CSVs)  →  BigQuery (dataset)  →  BigQueryLoader  →  Excel Reports
                                                                     →  Flask (Cloud Run)
```

**Components:**

- **Cloud Storage Bucket** — Stores raw CSV uploads in `gs://your-bucket/`. This can later be replaced with direct BigQuery streaming ingestion or native data imports for production use cases.

- **BigQuery Dataset** — A dataset in your GCP project (e.g., `pharma_claims`) containing five tables: `claims`, `members`, `drugs`, `plans`, `pharmacies`. Each table is loaded from its CSV with the same schema as the local files. BigQuery provides serverless SQL execution and built-in support for analytics workloads.

- **BigQueryLoader** — Implementation of the `DataLoader` interface in `src/ingestion/bigquery_loader.py`. Replaces CSVLoader when `PHARMA_DATA_SOURCE=bigquery`. Queries BigQuery and returns DataFrames, transparently to callers.

- **Excel Reports** — Unchanged. Calls `run_query(sql)` and receives a DataFrame. The query now executes on BigQuery instead of DuckDB, but the report generation code is identical.

- **Flask Dashboard on Cloud Run** — The Flask app (`src/dashboard/`) containerized and deployed to Google Cloud Run. Cloud Run provides serverless hosting, auto-scaling, and integration with Cloud IAM and monitoring.

- **Cloud Scheduler** *(optional)* — Schedule the Excel report pipeline (`python -m src.reports.excel.generate --report all`) to run automatically on a cron schedule for daily or weekly delivery.

## 4. Migration Steps

1. **Create a GCP project** — Enable the BigQuery API and Cloud Storage API in the [GCP Console](https://console.cloud.google.com/). Create a service account if using automated authentication; otherwise, prepare to use `gcloud auth application-default login` for local testing.

2. **Create a Cloud Storage bucket** — Create a bucket (e.g., `gs://pharma-claims-data/`) and upload the five CSV files from `data/`.

3. **Create a BigQuery dataset** — In your GCP project, create a dataset (e.g., `pharma_claims`). Create five tables by loading each CSV file:
   - `claims.csv` → `claims` table
   - `members.csv` → `members` table
   - `drugs.csv` → `drugs` table
   - `plans.csv` → `plans` table
   - `pharmacies.csv` → `pharmacies` table

   BigQuery auto-detects schemas; review them to ensure data types match your expectations (e.g., `service_date` should be DATE or TIMESTAMP).

4. **Install dependencies** — Add to `requirements.txt`:
   ```
   google-cloud-bigquery
   google-auth
   db-dtypes
   ```
   Then run `pip install -r requirements.txt`.

5. **Set environment variables** — Configure:
   ```bash
   export PHARMA_DATA_SOURCE=bigquery
   export GCP_PROJECT=your-gcp-project-id
   export GCP_DATASET=pharma_claims
   ```

6. **Authenticate** — Run `gcloud auth application-default login` to set up ADC (Application Default Credentials) for local development. For production (Cloud Run), assign a service account with BigQuery permissions.

7. **Implement BigQueryLoader** — Replace the `raise NotImplementedError` in `src/ingestion/bigquery_loader.py` with the implementation template already documented in the stub:
   ```python
   from google.cloud import bigquery

   client = bigquery.Client(project=config.GCP_PROJECT)
   table_ref = f"{config.GCP_PROJECT}.{config.GCP_DATASET}.{table_name}"
   query = f"SELECT * FROM `{table_ref}`"
   return client.query(query).to_dataframe()
   ```

8. **Test locally** — Run `python -m src.ingestion.db` to verify the data layer. Run a single report: `python -m src.reports.excel.generate --report claims_utilization`. Confirm the Excel file is generated and contains the expected data.

9. **Update the monthly_trend query** — The `monthly_trend` query in `src/sql/claims_utilization.sql` currently uses DuckDB's `STRFTIME` function. Change lines 46 and 52:
   ```sql
   -- Before (DuckDB):
   STRFTIME('%Y-%m', CAST(service_date AS DATE)) AS year_month

   -- After (BigQuery):
   FORMAT_DATE('%Y-%m', CAST(service_date AS DATE)) AS year_month
   ```

10. **Generate reports on BigQuery** — Run `python -m src.reports.excel.generate --report all` to generate all Excel reports using BigQuery as the backend.

11. *(Optional) Containerize for Cloud Run* — Create a `Dockerfile`:
    ```dockerfile
    FROM python:3.11-slim
    WORKDIR /app
    COPY . .
    RUN pip install -r requirements.txt
    CMD ["gunicorn", "--bind", "0.0.0.0:8080", "src.dashboard.app:app"]
    ```
    Build and push to Google Artifact Registry, then deploy to Cloud Run with environment variables set via the Cloud Run console.

## 5. SQL Compatibility Note

All ten queries across the project (`src/sql/`) are written in standard SQL compatible with both DuckDB and BigQuery:
- **claims_utilization.sql** — 3 queries: `status_summary`, `monthly_trend`, `plan_breakdown`
- **drug_cost.sql** — 4 queries: drug cost analysis
- **formulary_compliance.sql** — 3 queries: tier compliance metrics

**One exception:** The `monthly_trend` query uses `STRFTIME('%Y-%m', ...)` which is DuckDB-specific. BigQuery requires `FORMAT_DATE('%Y-%m', ...)` instead. This is the only dialect-specific change needed; all other queries run unchanged on BigQuery.

## 6. Key Design Decision

The project deliberately chose DuckDB as the local SQL engine because its SQL dialect is nearly identical to BigQuery's. This design decision ensures that **the migration is a configuration switch, not a rewrite**. A single environment variable change—`PHARMA_DATA_SOURCE=bigquery`—is sufficient to point the same report and dashboard code at BigQuery instead of CSVs. The `get_engine()` function in `src/ingestion/db.py` abstracts the loader selection, and `run_query(sql)` is the single interface both layers use. This keeps the codebase maintainable and demonstrates cloud-native thinking: build abstractly from the start so migrations are painless.
