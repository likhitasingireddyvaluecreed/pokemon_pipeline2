-- =====================================================
-- POKEMON DUCKDB DATABASE SCHEMA
-- =====================================================

-- =====================================================
-- TABLE: abilities
-- =====================================================
CREATE TABLE abilities (
    ability_name VARCHAR
);

-- =====================================================
-- TABLE: moves
-- =====================================================
CREATE TABLE moves (
    move_id BIGINT,
    move_name VARCHAR,
    move_type VARCHAR,
    power DOUBLE,
    accuracy DOUBLE,
    pp BIGINT,
    priority BIGINT,
    damage_class VARCHAR,
    generation VARCHAR
);

-- =====================================================
-- TABLE: pokemon
-- =====================================================
CREATE TABLE pokemon (
    pokemon_id BIGINT,
    pokemon_name VARCHAR,
    height_m DOUBLE,
    weight_kg DOUBLE,
    base_experience BIGINT,
    hp BIGINT,
    attack BIGINT,
    defense BIGINT,
    special_attack BIGINT,
    special_defense BIGINT,
    speed BIGINT
);

-- =====================================================
-- TABLE: pokemon_abilities
-- =====================================================
CREATE TABLE pokemon_abilities (
    pokemon_id BIGINT,
    ability_name VARCHAR,
    slot BIGINT,
    is_hidden BOOLEAN
);

-- =====================================================
-- TABLE: pokemon_moves
-- =====================================================
CREATE TABLE pokemon_moves (
    pokemon_id BIGINT,
    move_id BIGINT,
    move_name VARCHAR,
    learn_method VARCHAR,
    level_learned_at BIGINT,
    version_group VARCHAR
);

-- =====================================================
-- TABLE: pokemon_species
-- =====================================================
CREATE TABLE pokemon_species (
    pokemon_id BIGINT,
    pokemon_category VARCHAR,
    generation VARCHAR,
    color VARCHAR,
    shape VARCHAR,
    habitat VARCHAR,
    capture_rate BIGINT,
    base_happiness BIGINT,
    growth_rate VARCHAR,
    gender_rate BIGINT,
    hatch_counter BIGINT,
    egg_group_1 VARCHAR,
    egg_group_2 VARCHAR,
    is_baby BOOLEAN,
    is_legendary BOOLEAN,
    is_mythical BOOLEAN
);

-- =====================================================
-- TABLE: pokemon_types
-- =====================================================
CREATE TABLE pokemon_types (
    pokemon_id BIGINT,
    type_name VARCHAR,
    slot BIGINT
);

-- =====================================================
-- TABLE: pokemon_varieties
-- =====================================================
CREATE TABLE pokemon_varieties (
    species_id BIGINT,
    pokemon_id BIGINT,
    pokemon_name VARCHAR,
    is_default BOOLEAN
);

-- =====================================================
-- TABLE: types
-- =====================================================
CREATE TABLE types (
    type_name VARCHAR
);
