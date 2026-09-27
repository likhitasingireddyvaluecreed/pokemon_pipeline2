import duckdb
import logging

logger = logging.getLogger(__name__)

DUCKDB_FILE = "../pokemon.duckdb"


def retrieve_data():

    connection = duckdb.connect(
        DUCKDB_FILE
    )

    cursor = connection.cursor()

    try:

        logger.info(
            "Connected to DuckDB | database=%s",
            DUCKDB_FILE
        )

        # ============================================================
        # SHOW AVAILABLE SCHEMAS
        # ============================================================

        cursor.execute(
            """
            SHOW SCHEMAS
            """
        )

        schemas = cursor.fetchall()

        print("\nAVAILABLE SCHEMAS:")

        for schema in schemas:
            print(schema)

        # ============================================================
        # SHOW AVAILABLE TABLES
        # ============================================================

        cursor.execute(
            """
            SHOW TABLES
            """
        )

        tables = cursor.fetchall()

        print("\nAVAILABLE TABLES:")

        for table in tables:
            print(table)

        # ============================================================
        # RETRIEVE ONE RECORD
        # ============================================================

        cursor.execute(
            """
            SELECT *
            FROM pokemon
            LIMIT 1
            """
        )

        record = cursor.fetchone()

        print("\nONE RECORD:")

        print(record)

        # ============================================================
        # RETRIEVE MULTIPLE RECORDS
        # ============================================================

        cursor.execute(
            """
            SELECT *
            FROM pokemon
            LIMIT 5
            """
        )

        records = cursor.fetchmany(5)

        print("\nFIVE RECORDS:")

        for record in records:
            print(record)

        # ============================================================
        # RETRIEVE ALL RECORDS
        # ============================================================

        cursor.execute(
            """
            SELECT *
            FROM pokemon
            """
        )

        records = cursor.fetchall()

        print(
            f"\nTOTAL RECORDS RETRIEVED: {len(records)}"
        )

        # ============================================================
        # DISPLAY FIRST 10 RECORDS
        # ============================================================

        print("\nFIRST 10 RECORDS:")

        for record in records[:10]:
            print(record)

        logger.info(
            "Data retrieval completed successfully"
        )

    except Exception as e:

        logger.exception(
            "Data retrieval failed | error=%s",
            e
        )

        raise

    finally:

        cursor.close()

        connection.close()

        logger.info(
            "Cursor and DuckDB connection closed"
        )


if __name__ == "__main__":

    logging.basicConfig(
        level=logging.INFO
    )

    retrieve_data()