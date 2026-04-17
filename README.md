# Pharma Claims Analytics Portfolio

Automated pharmaceutical claims reporting and analytics — transforms manual Excel reports into a scalable data pipeline with a modern web dashboard.

**Python** • **Flask** • **DuckDB** • **pandas** • **openpyxl** • **Plotly.js**

## The Story

Pharmaceutical companies spend hours manually compiling claims data into Excel reports. This project automates that workflow: ingest raw claims data, run SQL analytics queries, and instantly generate publication-ready reports and dashboards.

When you run this project, you'll see:
- **Three automated Excel reports** capturing claims utilization, drug costs, and formulary compliance
- **A web dashboard** with interactive filtering, charts, and download links for Excel exports
- **BigQuery-ready architecture** — swap one config line to migrate from local CSV to cloud-scale analytics

This portfolio demonstrates the full technical stack expected in pharmaceutical data analytics: SQL proficiency, Python engineering, modern web UX, and cloud migration readiness.

## Quick Start

### Install dependencies
```bash
pip install -r requirements.txt
```

### Generate Excel reports
```bash
python -m src.reports.excel.generate --report all
```
Reports are saved to `/reports/output/`.

### Run the web dashboard
```bash
flask --app "src.dashboard.app:create_app" run --port 5000
```
Then open [http://localhost:5000](http://localhost:5000) in your browser.

### Run tests
```bash
python -m pytest tests/ -v
```

## Project Structure

| Directory | Purpose |
|-----------|---------|
| **data/** | Five CSV files: claims (800 rows), members (120), drugs (33), plans (4), pharmacies (8) |
| **src/ingestion/** | DataLoader abstraction layer — CSV today, BigQuery tomorrow |
| **src/sql/** | BigQuery-compatible SQL analytics queries (10 queries across 3 domains) |
| **src/reports/excel/** | Automated Excel report builders with formatting, charts, and multi-sheet layouts |
| **src/dashboard/** | Flask app factory and blueprint-based routes for claims, drugs, and formulary pages |
| **docs/** | Architecture and migration guides |
| **tests/** | Data layer tests |

## Report Pillars

### 1. Claims Utilization
- **Output**: Excel report + dashboard page
- **Metrics**: Paid/rejected/reversed claim rates, monthly trends, plan-level breakdowns
- **Use case**: Executive dashboard, plan performance reviews

### 2. Drug Cost Analysis
- **Output**: Excel report + dashboard page
- **Metrics**: Brand vs. generic spend, top 20 drugs, therapeutic class breakdown
- **Use case**: Formulary optimization, vendor negotiations

### 3. Formulary & Tier Compliance
- **Output**: Excel report + dashboard page
- **Metrics**: Tier adherence rates, generic fill rates, copay distribution
- **Use case**: Compliance audits, member education

## Google Cloud Migration

Swap one environment variable to scale from local CSV to BigQuery:

```bash
PHARMA_DATA_SOURCE=bigquery GCP_PROJECT=my-project GCP_DATASET=pharma_claims \
  python -m src.reports.excel.generate --report all
```

The `src/ingestion/` abstraction layer handles all data source switching. Reference `docs/gcp_architecture.md` for the full BigQuery migration design.

---

**Author**: Daniel Jung | **Created**: April 2026 | **Purpose**: Senior Data Analyst portfolio
