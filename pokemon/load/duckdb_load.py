import logging
import pandas as pd
import dlt

logger = logging.getLogger(__name__)


def load_dataframe_to_duckdb(
    df,
    table_name,
    primary_key
):

    if df.empty:

        logger.warning(
            "Skipping empty dataframe | table=%s",
            table_name
        )

        return

    logger.info(
        "Loading dataframe to DuckDB | table=%s | rows=%s",
        table_name,
        len(df)
    )

    pipeline = dlt.pipeline(
        pipeline_name="pokemon_processed",
        destination="duckdb",
        dataset_name="processed"
    )

    resource = dlt.resource(
        df.to_dict(
            orient="records"
        ),
        name=table_name,
        primary_key=primary_key,
        write_disposition="merge"
    )

    info = pipeline.run(
        resource
    )

    logger.info(
        "Data loaded successfully | table=%s",
        table_name
    )

    return info