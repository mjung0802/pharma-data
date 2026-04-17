"""
CSV-backed implementation of DataLoader.

Reads each table from a local CSV file under ``config.DATA_DIR``.
This is the default loader used during development and portfolio demos.
"""

import pandas as pd

from src import config
from src.ingestion.base import DataLoader, TABLES


# Map canonical table name → CSV filename (without the directory prefix so
# the mapping stays readable even if filenames ever diverge from table names).
_TABLE_FILES: dict[str, str] = {
    "claims": "claims.csv",
    "members": "members.csv",
    "drugs": "drugs.csv",
    "plans": "plans.csv",
    "pharmacies": "pharmacies.csv",
}


class CSVLoader(DataLoader):
    """Load tables from CSV files stored in ``config.DATA_DIR``."""

    def load(self, table_name: str) -> pd.DataFrame:
        """
        Read *table_name* from the corresponding CSV file.

        Parameters
        ----------
        table_name:
            One of: ``claims``, ``members``, ``drugs``, ``plans``,
            ``pharmacies``.

        Returns
        -------
        pd.DataFrame

        Raises
        ------
        ValueError
            If *table_name* is not one of the known table names.
        FileNotFoundError
            If the expected CSV file does not exist under ``DATA_DIR``.
        """
        self._validate_table(table_name)

        csv_path = config.DATA_DIR / _TABLE_FILES[table_name]
        return pd.read_csv(csv_path)
