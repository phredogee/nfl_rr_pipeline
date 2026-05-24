-- NFL RR Pipeline Database Schema
-- Tables: schedules, rosters, weekly_stats
-- Run this once to initialize the database structure

-- Drop tables if they exist (useful for clean resets during dev)
DROP TABLE IF EXISTS weekly_stats;
DROP TABLE IF EXISTS rosters;
DROP TABLE IF EXISTS schedules;

-- Schedule table: one row per game
CREATE TABLE schedules (
    game_id         VARCHAR(20) PRIMARY KEY,  -- unique game identifier
    season          INTEGER NOT NULL,          -- e.g. 2024
    game_type       VARCHAR(10),               -- REG, POST, PRE
    week            INTEGER,                   -- week number
    gameday         DATE,                      -- date of game
    weekday         VARCHAR(10),               -- e.g. Sunday
    gametime        VARCHAR(10),               -- kickoff time
    away_team       VARCHAR(10),               -- team abbreviation
    home_team       VARCHAR(10),               -- team abbreviation
    away_score      INTEGER,                   -- final score
    home_score      INTEGER,                   -- final score
    stadium         VARCHAR(100),              -- venue name
    roof            VARCHAR(20),               -- dome, outdoors, etc.
    surface         VARCHAR(20),               -- grass, turf, etc.
    temp            FLOAT,                     -- temperature at kickoff
    wind            FLOAT                      -- wind speed at kickoff
);

-- Roster table: one row per player per season
CREATE TABLE rosters (
    player_id       VARCHAR(20),               -- unique player identifier
    season          INTEGER NOT NULL,          -- e.g. 2024
    team            VARCHAR(10),               -- team abbreviation
    position        VARCHAR(10),               -- QB, RB, WR, etc.
    depth_chart_position VARCHAR(10),          -- more specific position
    jersey_number   INTEGER,
    full_name       VARCHAR(100),
    birth_date      DATE,
    height          VARCHAR(10),               -- e.g. 6-2
    weight          INTEGER,                   -- in pounds
    college         VARCHAR(100),
    years_exp       INTEGER,                   -- years of experience
    status          VARCHAR(20),               -- ACT, INA, etc.
    PRIMARY KEY (player_id, season, team)      -- player can switch teams
);

-- Weekly stats table: one row per player per week
CREATE TABLE weekly_stats (
    player_id       VARCHAR(20),               -- links to rosters
    player_name     VARCHAR(100),
    season          INTEGER NOT NULL,
    week            INTEGER NOT NULL,
    season_type     VARCHAR(10),               -- REG, POST
    team            VARCHAR(10),
    opponent        VARCHAR(10),
    position        VARCHAR(10),
    -- Passing
    completions     INTEGER,
    attempts        INTEGER,
    passing_yards   FLOAT,
    passing_tds     INTEGER,
    interceptions   INTEGER,
    -- Rushing
    carries         INTEGER,
    rushing_yards   FLOAT,
    rushing_tds     INTEGER,
    -- Receiving
    targets         INTEGER,
    receptions      INTEGER,
    receiving_yards FLOAT,
    receiving_tds   INTEGER,
    -- Misc
    fantasy_points  FLOAT,                     -- standard scoring
    fantasy_points_ppr FLOAT,                  -- PPR scoring
    PRIMARY KEY (player_id, season, week, team)
);