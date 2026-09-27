import time

from pokemon.extract.extract import (
    create_session,
    get_pokemon,
    extract_pokemon,
    extract_species,
    get_move,
    extract_moves
)

from pokemon.logging.logger import setup_logger
from pokemon.transform.transform_runner import run_transformation
from pokemon.load.load_raw import upsert_to_parquet

from pokemon.load.duckdb_load import (
    load_dataframe_to_duckdb
)




def main():
    """
    main file where extraction , transformation , load happens
    """

    #recording start time
    start_time = time.perf_counter()

    #setting up logger
    logger = setup_logger()

    try:

        logger.info("=" * 70)
        logger.info("POKEMON ETL PIPELINE STARTED")
        logger.info("=" * 70)

        # SESSION creation
        session = create_session()

        # discovering pokemon dataset urls
        logger.info("Discovering Pokemon resources")
#============================= EXTRACTION ================================================================
        #from extract module getting pokemon urls
        pokemon_urls, failed_pages = get_pokemon(
            session,
            logger
        )

        logger.info(
            "Pokemon URLs discovered | count=%s",
            len(pokemon_urls)
        )

        # from extract module extracting pokemon deails from the url
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

        # saving the pokemon data into parquet (from load_raw module upsert_to_parquet function also ensure's idempotency)
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

        # from extract module we are extracting species data from the urls
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

        # saving the pokemon species data into parquet (from load_raw module upsert_to_parquet function also ensure's idempotency)
        upsert_to_parquet(
            species_data,
            "species",
            primary_key="id"
        )

        # from extract module get the move urls
        move_urls = get_move(
            pokemon_data
        )

        logger.info(
            "Move resources discovered | count=%s",
            len(move_urls)
        )

        # from extract module , extract move data from the move urls
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

        # saving the pokemon move data into parquet (from load_raw module upsert_to_parquet function also ensure's idempotency)
        upsert_to_parquet(
            move_data,
            "moves",
            primary_key="id"
        )

#========================================= TRANSFORMATION ==================================================
        
        try:

            #from transformation_runner module get the run_transformation file where we store transformed data 
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

#================================ LOADING ===================================================================

        logger.info(
            "Saving processed datasets to DuckDB"
        )

        try:

            load_dataframe_to_duckdb(
                pokemon_df,
                "pokemon",
                "pokemon_id"
            )

            load_dataframe_to_duckdb(
                types_df,
                "pokemon_types",
                ["pokemon_id", "type_name"]
            )

            load_dataframe_to_duckdb(
                abilities_df,
                "pokemon_abilities",
                ["pokemon_id", "ability_name"]
            )

            load_dataframe_to_duckdb(
                species_df,
                "pokemon_species",
                "pokemon_id"
            )

            load_dataframe_to_duckdb(
                varieties_df,
                "pokemon_varieties",
                ["species_id", "pokemon_id"]
            )

            load_dataframe_to_duckdb(
                types_dimension_df,
                "types",
                "type_name"
            )

            load_dataframe_to_duckdb(
                abilities_dimension_df,
                "abilities",
                "ability_name"
            )

            load_dataframe_to_duckdb(
                moves_df,
                "moves",
                "move_id"
            )

            load_dataframe_to_duckdb(
                pokemon_moves_df,
                "pokemon_moves",
                ["pokemon_id", "move_id", "version_group"]
            )

            logger.info(
                "All processed datasets saved to DuckDB"
            )

        except Exception as e:

            logger.exception(
                "DuckDB loading failed | error=%s",
                e
            )

            raise

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