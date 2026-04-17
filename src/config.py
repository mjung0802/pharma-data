"""
Central configuration for the pharma claims analytics project.

All environment-specific settings live here. Switch data sources by setting
the PHARMA_DATA_SOURCE environment variable — nothing else in the codebase
needs to change.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env if present (development convenience; no-op in production)
load_dotenv()

# ---------------------------------------------------------------------------
# Project root — the directory that contains this file's parent (src/)
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# ---------------------------------------------------------------------------
# Data source selection
# ---------------------------------------------------------------------------
# Set PHARMA_DATA_SOURCE=bigquery to switch away from local CSV files.
DATA_SOURCE: str = os.getenv("PHARMA_DATA_SOURCE", "csv")

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
DATA_DIR: Path = PROJECT_ROOT / "data"
OUTPUT_DIR: Path = PROJECT_ROOT / "output" / "excel"

# ---------------------------------------------------------------------------
# Google Cloud / BigQuery (unused until DATA_SOURCE == "bigquery")
# ---------------------------------------------------------------------------
GCP_PROJECT: str | None = os.getenv("GCP_PROJECT", None)
GCP_DATASET: str | None = os.getenv("GCP_DATASET", None)
