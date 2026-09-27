import time

from extract import (
    create_session,
    get_pokemon,
    extract_pokemon,
    extract_species,
    get_move,
    extract_moves
)

from logger import setup_logger
from load_raw import save_to_parquet
from transform_runner import run_transformation
from load_raw import upsert_to_parquet

from duckdb_load import (
    create_connection,
    save_dataframe_to_duckdb
)




def main():

    start_time = time.perf_counter()

    logger = setup_logger()

    try:

        logger.info("=" * 70)
        logger.info("POKEMON ETL PIPELINE STARTED")
        logger.info("=" * 70)

        # SESSION creation
        session = create_session()

        # discovering pokemon dataset urls
        logger.info("Discovering Pokemon resources")

        pokemon_urls, failed_pages = get_pokemon(
            session,
            logger
        )

        logger.info(
            "Pokemon URLs discovered | count=%s",
            len(pokemon_urls)
        )

        # extracting pokemons from the urls
        pokemon_data, failed_pokemon = extract_pokemon(
            session,
            pokemon_urls,
            logger
        )

        logger.info(
            "Pokemon extraction completed | success=%s | failed=%s",
            len(pokemon_data),
            len(failed_pokemon)
        )

        # saving the pokemon data into parquet
        upsert_to_parquet(
            pokemon_data,
            "pokemon",
            primary_key="id"
        )

        # discovering species data urls
        species_urls = list({
            pokemon["species"]["url"]
            for pokemon in pokemon_data
            if pokemon.get("species")
            and pokemon["species"].get("url")
        })

        logger.info(
            "Species resources discovered | count=%s",
            len(species_urls)
        )

        # extracting species from the url
        species_data, failed_species = extract_species(
            session,
            species_urls,
            logger
        )

        logger.info(
            "Species extraction completed | success=%s | failed=%s",
            len(species_data),
            len(failed_species)
        )

        # save the species data into parquet form
        upsert_to_parquet(
            species_data,
            "species",
            primary_key="id"
        )

        # discover the move urls
        move_urls = get_move(
            pokemon_data
        )

        logger.info(
            "Move resources discovered | count=%s",
            len(move_urls)
        )

        # extract move data from the move urls
        move_data, failed_moves = extract_moves(
            session,
            move_urls,
            logger
        )

        logger.info(
            "Move extraction completed | success=%s | failed=%s",
            len(move_data),
            len(failed_moves)
        )

        # save the move data into parquet
        upsert_to_parquet(
            move_data,
            "moves",
            primary_key="id"
        )

        try:

            (
                pokemon_df,
                types_df,
                abilities_df,
                species_df,
                varieties_df,
                types_dimension_df,
                abilities_dimension_df,
                moves_df,
                pokemon_moves_df
            ) = run_transformation(
                            logger
                        )

            logger.info(
                "Transformation and validation completed successfully"
            )

        except Exception as e:

            logger.exception(
                "Transformation pipeline failed | error=%s",
                e
            )

            raise

        # ============================================================
        # 13. SAVE PROCESSED DATA TO DUCKDB
        # ============================================================

        logger.info(
            "Saving processed datasets to DuckDB"
        )

        connection = create_connection()

        try:

            save_dataframe_to_duckdb(
                pokemon_df,
                "pokemon",
                connection
            )

            save_dataframe_to_duckdb(
                types_df,
                "pokemon_types",
                connection
            )

            save_dataframe_to_duckdb(
                abilities_df,
                "pokemon_abilities",
                connection
            )

            save_dataframe_to_duckdb(
                species_df,
                "pokemon_species",
                connection
            )

            save_dataframe_to_duckdb(
                varieties_df,
                "pokemon_varieties",
                connection
            )

            save_dataframe_to_duckdb(
                types_dimension_df,
                "types",
                connection
            )

            save_dataframe_to_duckdb(
                abilities_dimension_df,
                "abilities",
                connection
            )

            save_dataframe_to_duckdb(
                moves_df,
                "moves",
                connection
            )

            save_dataframe_to_duckdb(
                pokemon_moves_df,
                "pokemon_moves",
                connection
            )

            logger.info(
                "All processed datasets saved to DuckDB"
            )

        finally:

            connection.close()

            logger.info(
                "DuckDB connection closed"
            )

        # PIPELINE SUMMARY

        elapsed = time.perf_counter() - start_time

        logger.info("=" * 70)
        logger.info("PIPELINE COMPLETED")

        logger.info(
            "Pokemon | success=%s | failed=%s",
            len(pokemon_data),
            len(failed_pokemon)
        )

        logger.info(
            "Species | success=%s | failed=%s",
            len(species_data),
            len(failed_species)
        )

        logger.info(
            "Moves | success=%s | failed=%s",
            len(move_data),
            len(failed_moves)
        )

        logger.info(
            "Execution time = %.2f seconds",
            elapsed
        )

        logger.info("=" * 70)

    except Exception as e:

        logger.exception(
            "Pipeline failed | error=%s",
            e
        )

        raise


if __name__ == "__main__":
    main()