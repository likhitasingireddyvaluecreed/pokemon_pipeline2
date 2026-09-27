# raw_load.py

import os
import logging
from datetime import datetime

import pyarrow as pa
import pyarrow.parquet as pq


logger = logging.getLogger(__name__)


RAW_DIR = "raw"


# def save_to_parquet(data, resource_name):
#     """
#     Save raw API responses  Parquet file.

#     resource_name - pokemon / species / moves
#     """

#     #if no data present raise warning
#     if not data:
#         logger.warning(
#             "No data available for %s",
#             resource_name
#         )
#         return None
    
#     #creating a path for resouce name file
#     resource_dir = os.path.join(
#         RAW_DIR,
#         resource_name
#     )

#     #creating the file dir
#     os.makedirs(
#         resource_dir,
#         exist_ok=True
#     )

#     #create parquet file
#     file_path = os.path.join(
#         resource_dir,
#         f"{resource_name}.parquet"
#     )

#     try:

#         #converting the pylist (dict) -> pyarrow table 
#         table = pa.Table.from_pylist(data)

#         #converting the pyarrow table into parquet file
#         pq.write_table(
#             table,
#             file_path,
#             compression="snappy"
#         )

#         logger.info(
#             "Raw Parquet saved | resource=%s | records=%s | file=%s",
#             resource_name,
#             table.num_rows,
#             file_path
#         )

#         #if successfull creation return file path 
#         return file_path

#     except Exception as e:

#         logger.error(
#             "Failed to save Parquet | resource=%s | error=%s",
#             resource_name,
#             e
#         )

#         return None



def upsert_to_parquet(
    new_data,
    resource_name,
    primary_key="id"
) :
    """
    Incrementally add/update records in a single Parquet file.

    Behaviour:
        - File doesn't exist -> create it
        - New ID -> insert record
        - Existing ID -> update record
        - Same record -> no duplicate
    """

    #if there is no new data ,no need to modify it
    if not new_data:

        logger.warning(
            "No new data available | resource=%s",
            resource_name
        )

        return None
    
    #creating the raw directory if not present
    os.makedirs(
        RAW_DIR,
        exist_ok=True
    )

    #creating parquet file 
    file_path = os.path.join(
        RAW_DIR,
        f"{resource_name}.parquet"
    )

 
    #loading existing data from the parquet file

    existing_data = []

    #open the raw parquet file if present
    if os.path.exists(file_path):

        logger.info(
            "Existing Parquet found | resource=%s",
            resource_name
        )

        #get the parquet file as apache pyarrow table
        table = pq.read_table(
            file_path
        )

        #converting the pyarrow table data into dict
        existing_data = table.to_pylist()

        logger.info(
            "Existing records | resource=%s | count=%s",
            resource_name,
            len(existing_data)
        )

    #updating the existing data into more efficient form for upserting for idempotency 
    #data gets changed from { "key":"value"}-> {"key" :{"key":"value"} , "Key" :{"key":"value"}}
    existing_records = {
        record.get(primary_key): record
        for record in existing_data
        if record.get(primary_key) is not None
    }


    #keepig track of details
    inserted = 0
    updated = 0
    unchanged = 0

    #looping around new data extracted
    for record in new_data:

        #get the index 
        record_id = record.get(primary_key)

        #if the index is not present in new data give an warning and continue the loop ( dont break)
        if record_id is None:

            logger.warning(
                "Skipping record without primary key | resource=%s",
                resource_name
            )

            continue

        #if new data, insert
        if record_id not in existing_records:

            existing_records[record_id] = record

            inserted += 1

        #if updated data , update it
        elif existing_records[record_id] != record:

            existing_records[record_id] = record

            updated += 1

        #else no change in data
        else:

            unchanged += 1

    #final data set after updating inserting 
    final_data = list(
        existing_records.values()
    )

    #create pyarrow table from the python dict type
    table = pa.Table.from_pylist(
        final_data
    )

    #write the pyarrow table type back to parquet file
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

    #returning the file path
    return file_path