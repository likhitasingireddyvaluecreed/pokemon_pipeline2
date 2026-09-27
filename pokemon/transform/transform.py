import pandas as pd


STAT_COLUMNS = [
    "hp",
    "attack",
    "defense",
    "special_attack",
    "special_defense",
    "speed"
]



def transform_pokemon(pokemon):

    """
    transform pokemon data columns [ stat columns names transformed ] 
    and assign values to the stats
    """

    record = {
        "pokemon_id": pokemon.get("id"),
        "pokemon_name": pokemon.get("name"),
        "height_m": (
            pokemon.get("height", 0) / 10
        ),
        "weight_kg": (
            pokemon.get("weight", 0) / 10
        ),
        "base_experience":
            pokemon.get("base_experience")
    }

    for stat in STAT_COLUMNS:
        record[stat] = None

    # transforming stat column names
    for item in pokemon.get("stats", []):

        stat_name = (
            item["stat"]["name"]
            .replace("-", "_")
        )

        #assgning values to the stat columns
        if stat_name in STAT_COLUMNS:

            record[stat_name] = (
                item["base_stat"]
            )

    return record


def transform_data(pokemon_data):
    """
    calling in each pokemon in the pokemon dataset
    to go under the transformation in the function transform_pokemon
    """

    records = []

    for pokemon in pokemon_data:

        record = transform_pokemon(
            pokemon
        )

        records.append(record)

    return pd.DataFrame(records)



def transform_types(pokemon_data):
    """
    Create the Pokemon-to-type relationship dataset.
    As type is multi valued column , we want it to be as seperate table
    """

    records = []

    #for each pokemon in the pokemon dataset
    for pokemon in pokemon_data:
        pokemon_id = pokemon.get("id")

        for item in pokemon.get("types") or []:
            type_info = item.get("type") or {}

            #get type data and append to records
            records.append({
                "pokemon_id": pokemon_id,
                "type_name": type_info.get("name"),
                "slot": item.get("slot")
            })

    # converting the new data set into data frame to save as a table
    return pd.DataFrame(records)




def transform_abilities(pokemon_data):
    """
    Create the Pokemon-to-ability relationship dataset.
    because abilities is also an multivalued column 
    """

    records = []

    #for each pokemon i am looping inside the pokemon data and getting the data 
    for pokemon in pokemon_data:
        pokemon_id = pokemon.get("id")

        for item in pokemon.get("abilities") or []:
            ability_info = item.get("ability") or {}

            records.append({
                "pokemon_id": pokemon_id,
                "ability_name": ability_info.get("name"),
                "slot": item.get("slot"),
                "is_hidden": item.get("is_hidden")
            })

    return pd.DataFrame(records)




def get_english_genus(species):

    for item in species.get(
        "genera",
        []
    ):

        if item["language"]["name"] == "en":

            return item["genus"]

    return None

def get_nested_name(data, key):
    value = data.get(key)

    if isinstance(value, dict):
        return value.get("name")

    return None
def get_egg_group_names(species):

    egg_groups = species.get("egg_groups") or []

    egg_group_1 = None
    egg_group_2 = None

    if len(egg_groups) > 0:
        egg_group_1 = egg_groups[0].get("name")

    if len(egg_groups) > 1:
        egg_group_2 = egg_groups[1].get("name")

    return egg_group_1, egg_group_2



def transform_species(species_data):
    """
    transform species data according to a dataframe from the data we got from species endpoint
    """

    records = []

    #looping around the species data 
    for species in species_data:

        #get the egg group
        egg_group_1, egg_group_2 = get_egg_group_names(species)

        record = {
            "pokemon_id": species.get("id"),

            # get pokmon category/genus
            "pokemon_category": get_english_genus(species),

            #get pokemon generation
            "generation": get_nested_name(
                species,
                "generation"
            ),

            #get pokemon color
            "color": get_nested_name(
                species,
                "color"
            ),

            #get pokemon shape
            "shape": get_nested_name(
                species,
                "shape"
            ),

            #get pokemon habitat
            "habitat": get_nested_name(
                species,
                "habitat"
            ),

            # capture rate of species
            "capture_rate": species.get("capture_rate"),

            #base happiness of a specie
            "base_happiness": species.get(
                "base_happiness"
            ),

            # get growth rate of a specie
            "growth_rate": get_nested_name(
                species,
                "growth_rate"
            ),

            #get gender rate of a specie
            "gender_rate": species.get(
                "gender_rate"
            ),

            #get hatch counter of a specie
            "hatch_counter": species.get(
                "hatch_counter"
            ),

            #write the data in format
            "egg_group_1": egg_group_1,
            "egg_group_2": egg_group_2,

            # get special status information
            "is_baby": species.get(
                "is_baby"
            ),

            "is_legendary": species.get(
                "is_legendary"
            ),

            "is_mythical": species.get(
                "is_mythical"
            )
        }

        # appending the data of a record fetched from the species
        records.append(record)

    return pd.DataFrame(records)



def remove_duplicates(df):
    """
    removing duplicates from the given data frame
    """

    #tracking if any duplicat's delted 
    before = len(df)

    #fropping duplicates
    df = df.drop_duplicates(
        subset=["pokemon_id"]
    )

    #tracking how many duplicated deleted 
    after = len(df)

    print(
        "Duplicates removed:",
        before - after
    )

    return df


def convert_data_types(df):
    """
    convert the pokemon data frame data types
    """

    #record the numeric data type
    numeric_columns = [
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
    ]

    # converting all required numeric data types into numeric
    for column in numeric_columns:

        df[column] = pd.to_numeric(
            df[column],
            errors="coerce"
        )

    return df


def handle_missing_values(df):
    """
    handling missing values in a data frmae
    """

    #record categorical columns
    categorical_columns = [
        "pokemon_name"
    ]

    # filled missing values wth unknown
    df[categorical_columns] = (
        df[categorical_columns]
        .fillna("Unknown")
    )

    return df


def apply_business_rules(df):
    """
    checking whether the pokemon data set is valid or not 
    """

    # checking for the data frame in correct value
    # the columns with greater than 0 value and is not na 
    df = df[
        (df["pokemon_id"] > 0) &
        (df["height_m"] >= 0) &
        (df["weight_kg"] >= 0) &
        (
            df["base_experience"].isna() |
            (df["base_experience"] >= 0)
        )
    ]

    return df


def validate_stat_values(df):
    """
    stat values need to be greater than 0
    """

    for column in STAT_COLUMNS:

        df = df[
            df[column].isna() |
            (df[column] >= 0)
        ]

    return df


def clean_data(df):

    """
    calling all above cleaning transforming function
    """

    df = remove_duplicates(df)

    df = convert_data_types(df)

    df = handle_missing_values(df)

    df = apply_business_rules(df)

    df = validate_stat_values(df)

    return df


#==================================== dervied =====================================================

def add_total_base_stats(df):
    """
    sum of total base stats
    """
    df["total_base_stats"] = (
        df[STAT_COLUMNS].sum(axis=1)
    )

    return df


def add_offensive_power(df):
    """
    sum of attact and special attack stats
    """

    df["offensive_power"] = (
        df["attack"] +
        df["special_attack"]
    )

    return df


def add_defensive_power(df):
    """
    sum of defensive and special_defensice stats
    """

    df["defensive_power"] = (
        df["defense"] +
        df["special_defense"]
    )

    return df


def add_speed_percentile(df):
    """
    Getting speed percentile field by together comparing the speed values of all the data set 

    -> get a rank according the speed stat 
    -> pct=True makes the rank to be in 0 to 1 range
    -> multiply the rank with 100 
    -> round it up to 2 decimal points
    """

    df["speed_percentile"] = (
        df["speed"]
        .rank(pct=True)
        .mul(100)
        .round(2)
    )

    return df


def add_battle_style(df):
    """
    get the offensive power(attack , special attack) and defensive power (defensive , special defensvie)

    -> get difference between offensive and defensve powers
    -> if diff is greater than 20 , then the battle style of a pokemon if offensive
    -> if the diff is less than -20 , then the battle style is defensive
    -> if it is between -20 to 20 then it has an balanced battle style
    """

    difference = (
        df["offensive_power"] -
        df["defensive_power"]
    )

    df["battle_style"] = "Balanced"

    df.loc[
        difference > 20,
        "battle_style"
    ] = "Offensive"

    df.loc[
        difference < -20,
        "battle_style"
    ] = "Defensive"

    return df


def add_stat_specialization(df):
    """
    stat specialization is the value where the pokemon has which stat value as highest 
    """

    # get highest value stat column
    df["stat_specialization"] = (
        df[STAT_COLUMNS]
        .idxmax(axis=1)
    )

    return df


def add_size_class(df):

    """
    grouping pokemons into sized groups 

    -> get ranks of the pokemon heights and weights
    ->get the size score
    ->lets find the quantile for this size score
    # binning for labeling the groups
    """
    # 1. Get percentile ranks (0 to 1) for both attributes
    height_rank = df["height_m"].rank(pct=True)
    weight_rank = df["weight_kg"].rank(pct=True)
    
    # 2. Combine them into an overall size score
    size_score = (height_rank + weight_rank) / 2
    
    # 3. Find the true 33rd and 66th cutoffs of this combined score
    cutoff_33 = size_score.quantile(0.33)
    cutoff_66 = size_score.quantile(0.66)
    
    # 4. Assign categories cleanly using pd.cut
    import pandas as pd
    df["size_class"] = pd.cut(
        size_score,
        bins=[-1, cutoff_33, cutoff_66, 2],
        labels=["Small", "Medium", "Large"]
    )
    
    return df


def add_special_status(df):
    """
    add special status from the species data set 

    -> normal intially
    -> if is baby is true then baby
    -> if is legendary is true then legendary
    -> if is mythical is true then mythical
    """

    df["special_status"] = "Normal"

    df.loc[
        df["is_baby"] == True,
        "special_status"
    ] = "Baby"

    df.loc[
        df["is_legendary"] == True,
        "special_status"
    ] = "Legendary"

    df.loc[
        df["is_mythical"] == True,
        "special_status"
    ] = "Mythical"

    return df

def merge_species_attributes(
    pokemon_df,
    species_df
):
    """
    another table where we merge species data with pokemon data 
    """

    species_columns = [
        "pokemon_id",
        "is_baby",
        "is_legendary",
        "is_mythical"
    ]

    species_status = species_df[
        species_columns
    ]

    # merging pokemon and species data
    pokemon_df = pokemon_df.merge(
        species_status,
        on="pokemon_id",
        how="left"
    )

    return pokemon_df

def add_derived_attributes(df):
    """
    calling all derived data columns to be added
    """

    df = add_total_base_stats(df)

    df = add_offensive_power(df)

    df = add_defensive_power(df)

    df = add_speed_percentile(df)

    df = add_battle_style(df)

    df = add_stat_specialization(df)

    df = add_size_class(df)

    df = add_special_status(df)

    return df


def transform_varieties(species_data):
    """
    get varieties data from the species data set and write it in the pokemon varieties data frame

    we will add a column where we have True or False value
    which shows that whether it is a variety of an pokemon or is it a form
    """
    records = []

    for species in species_data:
        species_id = species.get("id")

        for variety in species.get("varieties") or []:
            pokemon = variety.get("pokemon") or {}
            pokemon_url = pokemon.get("url")

            pokemon_id = None
            if pokemon_url:
                pokemon_id = int(
                    pokemon_url.rstrip("/").split("/")[-1]
                )

            records.append({
                "species_id": species_id,
                "pokemon_id": pokemon_id,
                "pokemon_name": pokemon.get("name"),
                "is_default": variety.get("is_default")
            })

    return pd.DataFrame(records)

def transform_types_dimension(pokemon_data):
    """
    Create a unique type dimension dataset.
    """

    types = set()

    for pokemon in pokemon_data:
        for item in pokemon.get("types") or []:
            type_info = item.get("type") or {}
            type_name = type_info.get("name")

            if type_name:
                types.add(type_name)

    records = [
        {
            "type_name": type_name
        }
        for type_name in sorted(types)
    ]

    return pd.DataFrame(records)


def transform_abilities_dimension(pokemon_data):
    """
    Create a unique ability dimension dataset.
    """

    abilities = set()

    for pokemon in pokemon_data:
        for item in pokemon.get("abilities") or []:
            ability_info = item.get("ability") or {}
            ability_name = ability_info.get("name")

            if ability_name:
                abilities.add(ability_name)

    records = [
        {
            "ability_name": ability_name
        }
        for ability_name in sorted(abilities)
    ]

    return pd.DataFrame(records)

############ moves ##################################

def transform_moves(move_data):
    """
    Transform raw move API responses into the move dimension.
    """

    records = []

    for move in move_data:

        type_info = move.get("type") or {}
        damage_class_info = move.get("damage_class") or {}
        generation_info = move.get("generation") or {}

        records.append({
            "move_id": move.get("id"),
            "move_name": move.get("name"),
            "move_type": type_info.get("name"),
            "power": move.get("power"),
            "accuracy": move.get("accuracy"),
            "pp": move.get("pp"),
            "priority": move.get("priority"),
            "damage_class": damage_class_info.get("name"),
            "generation": generation_info.get("name")
        })

    return pd.DataFrame(records)

def transform_pokemon_moves(pokemon_data):
    """
    Create the Pokemon-to-move relationship dataset.

    A Pokemon can learn many moves, and a move can be learned
    by many Pokémon.
    """

    records = []

    for pokemon in pokemon_data:

        pokemon_id = pokemon.get("id")

        for move_item in pokemon.get("moves") or []:

            move_info = move_item.get("move") or {}

            move_url = move_info.get("url")

            move_id = None

            if move_url:
                move_id = int(
                    move_url.rstrip("/").split("/")[-1]
                )

            for version_detail in (
                move_item.get("version_group_details") or []
            ):

                version_group = (
                    version_detail.get("version_group") or {}
                )

                move_learn_method = (
                    version_detail.get("move_learn_method") or {}
                )

                records.append({
                    "pokemon_id": pokemon_id,
                    "move_id": move_id,
                    "move_name": move_info.get("name"),
                    "learn_method": move_learn_method.get("name"),
                    "level_learned_at": version_detail.get(
                        "level_learned_at"
                    ),
                    "version_group": version_group.get("name")
                })

    return pd.DataFrame(records)