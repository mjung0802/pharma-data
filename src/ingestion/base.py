"""
Abstract base class for all data loaders.

Any new data source (CSV, BigQuery, Snowflake, …) must subclass DataLoader
and implement `load()`. The rest of the codebase depends only on this
interface, not on a concrete loader.
"""

from abc import ABC, abstractmethod

import pandas as pd


# Canonical table names — these match the CSV filenames (without extension)
# and are the names registered as DuckDB views in db.py.
TABLES = ("claims", "members", "drugs", "plans", "pharmacies")


class DataLoader(ABC):
    """Load a named table and return it as a pandas DataFrame."""

    def _validate_table(self, table_name: str) -> None:
        if table_name not in TABLES:
            raise ValueError(
                f"Unknown table '{table_name}'. Valid: {', '.join(sorted(TABLES))}"
            )

    @abstractmethod
    def load(self, table_name: str) -> pd.DataFrame:
        """
        Return the contents of *table_name* as a DataFrame.

        Parameters
        ----------
        table_name:
            One of the canonical table names defined in ``TABLES``.

        Returns
        -------
        pd.DataFrame
            All rows for the requested table.

        Raises
        ------
        ValueError
            If *table_name* is not recognised by this loader.
        NotImplementedError
            If the concrete subclass has not been fully implemented yet.
        """
