"""
BigQuery-backed implementation of DataLoader — STUB.

This file documents what the real implementation would look like but does NOT
attempt to connect to BigQuery. Set ``PHARMA_DATA_SOURCE=bigquery`` only after
you have completed the steps in the "To activate" section below.

To activate
-----------
1.  Install the BigQuery client library:
        pip install google-cloud-bigquery db-dtypes

2.  Set environment variables (or add them to .env):
        GCP_PROJECT=your-gcp-project-id
        GCP_DATASET=your_bq_dataset

3.  Authenticate:
        gcloud auth application-default login
    (or provide a service-account key via GOOGLE_APPLICATION_CREDENTIALS)

4.  Replace the ``load()`` body below with the real implementation shown in
    the comments.
"""

import pandas as pd

from src import config
from src.ingestion.base import DataLoader, TABLES


class BigQueryLoader(DataLoader):
    """Load tables from Google BigQuery."""

    def load(self, table_name: str) -> pd.DataFrame:
        """
        Return *table_name* from BigQuery as a DataFrame.

        NOT YET IMPLEMENTED — see module docstring for setup steps.

        Real implementation would look like:

            from google.cloud import bigquery  # pip install google-cloud-bigquery

            client = bigquery.Client(project=config.GCP_PROJECT)
            table_ref = f"{config.GCP_PROJECT}.{config.GCP_DATASET}.{table_name}"
            query = f"SELECT * FROM `{table_ref}`"
            return client.query(query).to_dataframe()

        Parameters
        ----------
        table_name:
            One of: ``claims``, ``members``, ``drugs``, ``plans``,
            ``pharmacies``.

        Raises
        ------
        NotImplementedError
            Always — this stub has not been wired up yet.
        """
        raise NotImplementedError(
            f"BigQueryLoader.load('{table_name}') is not implemented yet.\n"
            "To enable BigQuery connectivity you need to:\n"
            "  1. pip install google-cloud-bigquery db-dtypes\n"
            f"  2. Set GCP_PROJECT (currently: {config.GCP_PROJECT!r})\n"
            f"  3. Set GCP_DATASET (currently: {config.GCP_DATASET!r})\n"
            "  4. Authenticate via 'gcloud auth application-default login'\n"
            "  5. Replace the raise in this method with the real BQ query.\n"
            "See the module docstring in bigquery_loader.py for the full "
            "implementation template."
        )
