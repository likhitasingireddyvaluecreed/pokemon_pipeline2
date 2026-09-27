import dlt

from dlt.sources.filesystem import (
    filesystem,
    read_parquet
)


def load_parquet_to_duckdb(
    resource_name,
    primary_key
):

    files = filesystem(
        bucket_url=f"file://./raw/{resource_name}",
        file_glob="*.parquet",
        incremental=dlt.sources.incremental(
            "modification_date"
        )
    )

    resource = files | read_parquet()

    resource = resource.with_name(
        resource_name
    )

    resource.apply_hints(
        primary_key=primary_key
    )

    pipeline = dlt.pipeline(
        pipeline_name="pokemon_pipeline",
        destination="duckdb",
        dataset_name="raw"
    )

    info = pipeline.run(
        resource,
        write_disposition="merge"
    )

    return info