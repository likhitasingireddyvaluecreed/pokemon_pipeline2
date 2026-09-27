# raw_load.py

import os
import logging
from datetime import datetime

import pyarrow as pa
import pyarrow.parquet as pq


logger = logging.getLogger(__name__)


RAW_DIR = "raw"


def save_to_parquet(data, resource_name):
    """
    Save raw API responses into a timestamped Parquet file.

    resource_name:
        pokemon / species / moves
    """

    if not data:
        logger.warning(
            "No data available for %s",
            resource_name
        )
        return None

    resource_dir = os.path.join(
        RAW_DIR,
        resource_name
    )

    os.makedirs(
        resource_dir,
        exist_ok=True
    )

    timestamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )

    file_path = os.path.join(
        resource_dir,
        f"{resource_name}_{timestamp}.parquet"
    )

    try:

        table = pa.Table.from_pylist(data)

        pq.write_table(
            table,
            file_path,
            compression="snappy"
        )

        logger.info(
            "Raw Parquet saved | resource=%s | records=%s | file=%s",
            resource_name,
            table.num_rows,
            file_path
        )

        return file_path

    except Exception as e:

        logger.error(
            "Failed to save Parquet | resource=%s | error=%s",
            resource_name,
            e
        )

        return None



def upsert_to_parquet(
    new_data,
    resource_name,
    primary_key="id"
):
    """
    Incrementally add/update records in a single Parquet file.

    Behaviour:
        - File doesn't exist -> create it
        - New ID -> insert record
        - Existing ID -> update record
        - Same record -> no duplicate
    """

    if not new_data:

        logger.warning(
            "No new data available | resource=%s",
            resource_name
        )

        return None

    os.makedirs(
        RAW_DIR,
        exist_ok=True
    )

    file_path = os.path.join(
        RAW_DIR,
        f"{resource_name}.parquet"
    )

    # ============================================================
    # LOAD EXISTING DATA
    # ============================================================

    existing_data = []

    if os.path.exists(file_path):

        logger.info(
            "Existing Parquet found | resource=%s",
            resource_name
        )

        table = pq.read_table(
            file_path
        )

        existing_data = table.to_pylist()

        logger.info(
            "Existing records | resource=%s | count=%s",
            resource_name,
            len(existing_data)
        )

    # ============================================================
    # CREATE INDEX FROM EXISTING DATA
    # ============================================================

    existing_records = {
        record.get(primary_key): record
        for record in existing_data
        if record.get(primary_key) is not None
    }

    # ============================================================
    # UPSERT NEW DATA
    # ============================================================

    inserted = 0
    updated = 0
    unchanged = 0

    for record in new_data:

        record_id = record.get(primary_key)

        if record_id is None:

            logger.warning(
                "Skipping record without primary key | resource=%s",
                resource_name
            )

            continue

        if record_id not in existing_records:

            existing_records[record_id] = record

            inserted += 1

        elif existing_records[record_id] != record:

            existing_records[record_id] = record

            updated += 1

        else:

            unchanged += 1

    # ============================================================
    # FINAL DATASET
    # ============================================================

    final_data = list(
        existing_records.values()
    )

    # ============================================================
    # WRITE SINGLE PARQUET FILE
    # ============================================================

    table = pa.Table.from_pylist(
        final_data
    )

    pq.write_table(
        table,
        file_path,
        compression="snappy"
    )

    logger.info(
        "Parquet upsert completed | "
        "resource=%s | inserted=%s | updated=%s | unchanged=%s | total=%s",
        resource_name,
        inserted,
        updated,
        unchanged,
        len(final_data)
    )

    return file_path