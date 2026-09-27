import os
import logging

import pandas as pd
import pyarrow.parquet as pq
from transform import (
    transform_data,
    transform_types,
    transform_types_dimension,
    transform_abilities,
    transform_abilities_dimension,
    transform_species,
    transform_varieties,
    transform_moves,
    transform_pokemon_moves
)

from pokemon.validation.validation import (
    validate_dataframe,
    validate_unique_key,
    validate_non_negative
)


logger = logging.getLogger(__name__)

RAW_DIR = "raw"


def load_parquet(resource_name):
    """
    Load the complete raw Parquet dataset
    as normal Python list[dict] records.
    """

    #get the path of parquet file
    file_path = os.path.join(
        RAW_DIR,
        f"{resource_name}.parquet"
    )

    #if file note present raise error
    if not os.path.exists(file_path):

        raise FileNotFoundError(
            f"Parquet file not found: {file_path}"
        )

    logger.info(
        "Reading raw Parquet | resource=%s | file=%s",
        resource_name,
        file_path
    )

    #get the parquet file data as pyarrow table
    table = pq.read_table(
        file_path
    )

    #convert the pyarrow into dict
    records = table.to_pylist()

    logger.info(
        "Raw data loaded | resource=%s | records=%s",
        resource_name,
        len(records)
    )

    #return the parquet file data as dict records
    return records


def run_transformation(logger):
    """
    Calls all the transformation functions from the transform module 
    Also call all vaidation functions from the validation module

    Purpose: to increase code redability
    """

    logger.info("=" * 70)
    logger.info("STARTING RAW PARQUET LOAD")
    logger.info("=" * 70)

    #loading raw parquet files to transform
    pokemon_data = load_parquet(
    "pokemon"
    )

    species_data = load_parquet(
        "species"
    )

    move_data = load_parquet(
        "moves"
    )

    logger.info(
        "Raw data ready for transformation | "
        "pokemon=%s | species=%s | moves=%s",
        len(pokemon_data),
        len(species_data),
        len(move_data)
    )

#================================= strating transformation =======================================

    logger.info(
        "Starting transformation layer"
    )

    pokemon_df = transform_data(
        pokemon_data
    )

    print(type(pokemon_data))
    print(type(pokemon_data[0]))
    print(type(pokemon_data[0]["types"]))

    types_df = transform_types(
        pokemon_data
    )

    types_dimension_df = transform_types_dimension(
        pokemon_data
    )

    abilities_df = transform_abilities(
        pokemon_data
    )

    abilities_dimension_df = transform_abilities_dimension(
        pokemon_data
    )

    species_df = transform_species(
        species_data
    )

    varieties_df = transform_varieties(
        species_data
    )

    moves_df = transform_moves(
        move_data
    )

    pokemon_moves_df = transform_pokemon_moves(
        pokemon_data
    )

    logger.info(
        "Transformation completed"
    )


    # TRANSFORMATION SUMMARY
   

    logger.info(
        "pokemon_df | rows=%s | columns=%s",
        len(pokemon_df),
        len(pokemon_df.columns)
    )

    logger.info(
        "types_df | rows=%s | columns=%s",
        len(types_df),
        len(types_df.columns)
    )

    logger.info(
        "types_dimension_df | rows=%s | columns=%s",
        len(types_dimension_df),
        len(types_dimension_df.columns)
    )

    logger.info(
        "abilities_df | rows=%s | columns=%s",
        len(abilities_df),
        len(abilities_df.columns)
    )

    logger.info(
        "abilities_dimension_df | rows=%s | columns=%s",
        len(abilities_dimension_df),
        len(abilities_dimension_df.columns)
    )

    logger.info(
        "species_df | rows=%s | columns=%s",
        len(species_df),
        len(species_df.columns)
    )

    logger.info(
        "varieties_df | rows=%s | columns=%s",
        len(varieties_df),
        len(varieties_df.columns)
    )

    logger.info(
        "moves_df | rows=%s | columns=%s",
        len(moves_df),
        len(moves_df.columns)
    )

    logger.info(
        "pokemon_moves_df | rows=%s | columns=%s",
        len(pokemon_moves_df),
        len(pokemon_moves_df.columns)
    )

# ================================ VALIDATION =======================================================

    logger.info(
        "Starting validation layer"
    )

    #pokemon dataset validation

    validate_dataframe(
        pokemon_df,
        [
            "pokemon_id",
            "pokemon_name",
            "height_m",
            "weight_kg",
            "base_experience"
        ],
        "pokemon",
        logger
    )

    validate_unique_key(
        pokemon_df,
        "pokemon_id",
        "pokemon",
        logger
    )

    validate_non_negative(
        pokemon_df,
        [
            "pokemon_id",
            "height_m",
            "weight_kg",
            "base_experience",
            "hp",
            "attack",
            "defense",
            "special_attack",
            "special_defense",
            "speed"
        ],
        "pokemon",
        logger
    )

    # Species dataset validation


    validate_dataframe(
        species_df,
        [
            "pokemon_id",
            "pokemon_category",
            "generation"
        ],
        "pokemon_species",
        logger
    )

    validate_unique_key(
        species_df,
        "pokemon_id",
        "pokemon_species",
        logger
    )

    logger.info(
        "All validations passed"
    )


    # RETURN TRANSFORMED DATA


    return (
            pokemon_df,
            types_df,
            abilities_df,
            species_df,
            varieties_df,
            types_dimension_df,
            abilities_dimension_df,
            moves_df,
            pokemon_moves_df
        )

