import duckdb
import logging

logger = logging.getLogger(__name__)

DUCKDB_FILE = "pokemon.duckdb"
SCHEMA_FILE = "schema.txt"


def generate_schema():

    connection = duckdb.connect(
        DUCKDB_FILE
    )

    try:

        logger.info(
            "Connected to DuckDB | database=%s",
            DUCKDB_FILE
        )

        # Get all tables
        tables = connection.execute(
            """
            SHOW TABLES
            """
        ).fetchall()

        if not tables:

            logger.warning(
                "No tables found in DuckDB"
            )

            return

        schema_output = []

        for table in tables:

            table_name = table[0]

            schema_output.append(
                "\n" + "=" * 70
            )

            schema_output.append(
                f"TABLE: {table_name}"
            )

            schema_output.append(
                "=" * 70
            )

            # Get table schema
            columns = connection.execute(
                f"""
                DESCRIBE "{table_name}"
                """
            ).fetchall()

            schema_output.append(
                f"{'COLUMN':<30}"
                f"{'TYPE':<25}"
                f"{'NULLABLE'}"
            )

            schema_output.append(
                "-" * 70
            )

            for column in columns:

                column_name = column[0]
                data_type = column[1]
                null_value = column[2]

                schema_output.append(
                    f"{column_name:<30}"
                    f"{data_type:<25}"
                    f"{null_value}"
                )

        # Convert list into one text
        schema_text = "\n".join(
            schema_output
        )

        # Print schema in terminal
        print(
            schema_text
        )

        # Save same output to file
        with open(
            SCHEMA_FILE,
            "w",
            encoding="utf-8"
        ) as file:

            file.write(
                schema_text
            )

        logger.info(
            "Schema saved successfully | file=%s",
            SCHEMA_FILE
        )

    finally:

        connection.close()

        logger.info(
            "DuckDB connection closed"
        )


if __name__ == "__main__":

    logging.basicConfig(
        level=logging.INFO
    )

    generate_schema()