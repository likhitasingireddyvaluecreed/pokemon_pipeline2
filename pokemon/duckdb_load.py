import duckdb
import logging
import pandas as pd


logger = logging.getLogger(__name__)

DUCKDB_FILE = "pokemon.duckdb"


def save_dataframe_to_duckdb(
    df: pd.DataFrame,
    table_name: str,
    connection
):
    """
    Save a Pandas DataFrame into DuckDB.

    If the table does not exist:
        create it.

    If the table already exists:
        replace its contents.
    """

    if df.empty:
        logger.warning(
            "Skipping empty dataframe | table=%s",
            table_name
        )
        return

    logger.info(
        "Saving dataframe to DuckDB | table=%s | rows=%s",
        table_name,
        len(df)
    )

    connection.register(
        "temp_dataframe",
        df
    )

    connection.execute(
        f"""
        CREATE OR REPLACE TABLE "{table_name}" AS
        SELECT *
        FROM temp_dataframe
        """
    )

    connection.unregister(
        "temp_dataframe"
    )

    logger.info(
        "DuckDB table saved successfully | table=%s | rows=%s",
        table_name,
        len(df)
    )


def create_connection():
    """
    Create DuckDB connection.
    """

    connection = duckdb.connect(
        DUCKDB_FILE
    )

    logger.info(
        "Connected to DuckDB | database=%s",
        DUCKDB_FILE
    )

    return connection