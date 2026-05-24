# ingest.py
# Pulls NFL data via nfl_data_py and loads it into Postgres
# Run this once to backfill historical data, then on a schedule for live updates

import nfl_data_py as nfl
import pandas as pd
import psycopg2
from psycopg2.extras import execute_values  # bulk insert helper, much faster than row-by-row
import sys
import os

# Allow imports from the config folder regardless of where script is run from
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'config'))
from db_config import DB_CONFIG

# ── Helpers ───────────────────────────────────────────────────────────────────

def get_connection():
    """Create and return a Postgres connection using DB_CONFIG."""
    return psycopg2.connect(**DB_CONFIG)


def clean_df(df, required_cols):
    """
    Keep only the columns we care about and replace NaN with None.
    None maps to SQL NULL; NaN does not and causes insert errors.
    """
    existing = [c for c in required_cols if c in df.columns]
    df = df[existing].copy()
    df = df.where(pd.notnull(df), None)  # NaN → None
    df = df.replace({pd.NaT: None})      # NaT (null datetime) → None
   
    return df


# ── Schedules ─────────────────────────────────────────────────────────────────

def ingest_schedules(seasons: list[int]):
    print(f"\n📅 Ingesting schedules for seasons: {seasons}")
    df = nfl.import_schedules(seasons)

    print(f"   Raw shape: {df.shape} | dtypes sample: {df.dtypes[['game_id','season','home_team']].to_dict()}")

    cols = [
        'game_id', 'season', 'game_type', 'week', 'gameday',
        'weekday', 'gametime', 'away_team', 'home_team',
        'away_score', 'home_score', 'stadium', 'roof', 'surface',
        'temp', 'wind'
    ]
    df = clean_df(df, cols)

    print(f"   Cleaned shape: {df.shape}")
    print(f"   Columns: {list(df.columns)}")

    rows = [tuple(row) for row in df.itertuples(index=False)]

    sql = """
        INSERT INTO schedules (
            game_id, season, game_type, week, gameday,
            weekday, gametime, away_team, home_team,
            away_score, home_score, stadium, roof, surface,
            temp, wind
        ) VALUES %s
        ON CONFLICT (game_id) DO NOTHING
    """
    # ON CONFLICT DO NOTHING = safe to re-run without duplicating rows

    with get_connection() as conn:
        with conn.cursor() as cur:
            execute_values(cur, sql, rows)
        conn.commit()

    print(f"   ✅ {len(rows)} schedule rows inserted.")


# ── Rosters ───────────────────────────────────────────────────────────────────

def ingest_rosters(seasons: list[int]):
    print(f"\n👥 Ingesting rosters for seasons: {seasons}")
    df = nfl.import_seasonal_rosters(seasons)

    print(f"   Available columns: {list(df.columns)}")
    print(f"   Raw shape: {df.shape} | dtypes sample: {df.dtypes[['player_id','season','team']].to_dict()}")

    cols = [
        'player_id', 'season', 'team', 'position',
        'jersey_number', 'player_name',
        'birth_date', 'height', 'weight', 'college',
        'years_exp', 'status'
    ]
    df = clean_df(df, cols)

    print(f"   Cleaned shape: {df.shape}")

    # Helper: safely convert to int, returning None for nulls or overflow
    def safe_int(val):
        try:
            if val is None or (isinstance(val, float) and pd.isna(val)):
                return None
            return int(val)
        except (ValueError, OverflowError):
            return None

    # Helper: safely convert to str, returning None for nulls
    def safe_str(val):
        if val is None or (isinstance(val, float) and pd.isna(val)):
            return None
        return str(val)

    # Build rows explicitly so every value is a native Python type
    rows = []
    for row in df.itertuples(index=False):
        rows.append((
            safe_str(row.player_id),
            safe_int(row.season),
            safe_str(row.team),
            safe_str(row.position),
            safe_int(row.jersey_number),
            safe_str(row.player_name),
            row.birth_date if row.birth_date is not None else None,
            safe_str(row.height),
            safe_int(row.weight),
            safe_str(row.college),
            safe_int(row.years_exp),
            safe_str(row.status),
        ))

    sql = """
        INSERT INTO rosters (
            player_id, season, team, position,
            jersey_number, full_name,
            birth_date, height, weight, college,
            years_exp, status
        ) VALUES %s
        ON CONFLICT (player_id, season, team) DO NOTHING
    """

    with get_connection() as conn:
        with conn.cursor() as cur:
            execute_values(cur, sql, rows)
        conn.commit()

    print(f"   ✅ {len(rows)} roster rows inserted.")



# ── Weekly Stats ──────────────────────────────────────────────────────────────

def ingest_weekly_stats(seasons: list[int]):
    print(f"\n📊 Ingesting weekly stats for seasons: {seasons}")
    df = nfl.import_weekly_data(seasons)

    print(f"   Raw shape: {df.shape} | dtypes sample: {df.dtypes[['player_id','season','week']].to_dict()}")
    print(f"   Available columns: {list(df.columns)}")

    cols = [
        'player_id', 'player_name', 'season', 'week', 'season_type',
        'recent_team', 'opponent_team', 'position',
        'completions', 'attempts', 'passing_yards', 'passing_tds', 'interceptions',
        'carries', 'rushing_yards', 'rushing_tds',
        'targets', 'receptions', 'receiving_yards', 'receiving_tds',
        'fantasy_points', 'fantasy_points_ppr'
    ]

    # Only keep columns that actually exist in the dataframe
    cols = [c for c in cols if c in df.columns]
    df = clean_df(df, cols)

    print(f"   Cleaned shape: {df.shape}")
    print(f"   Columns kept: {list(df.columns)}")

    # Helper: safely convert to int, returning None for nulls
    def safe_int(val):
        try:
            if val is None or (isinstance(val, float) and pd.isna(val)):
                return None
            return int(val)
        except (ValueError, OverflowError):
            return None

    # Helper: safely convert to float, returning None for nulls
    def safe_float(val):
        try:
            if val is None or (isinstance(val, float) and pd.isna(val)):
                return None
            return float(val)
        except (ValueError, OverflowError):
            return None

    # Helper: safely convert to str, returning None for nulls
    def safe_str(val):
        if val is None or (isinstance(val, float) and pd.isna(val)):
            return None
        return str(val)

    # Build rows explicitly using only columns that exist
    col_set = list(df.columns)
    rows = []
    for row in df.itertuples(index=False):
        d = dict(zip(col_set, row))
        rows.append((
            safe_str(d.get('player_id')),
            safe_str(d.get('player_name')),
            safe_int(d.get('season')),
            safe_int(d.get('week')),
            safe_str(d.get('season_type')),
            safe_str(d.get('recent_team')),    # was 'team'
            safe_str(d.get('opponent_team')),  # was 'opponent'
            safe_str(d.get('position')),
            safe_int(d.get('completions')),
            safe_int(d.get('attempts')),
            safe_float(d.get('passing_yards')),
            safe_int(d.get('passing_tds')),
            safe_int(d.get('interceptions')),
            safe_int(d.get('carries')),
            safe_float(d.get('rushing_yards')),
            safe_int(d.get('rushing_tds')),
            safe_int(d.get('targets')),
            safe_int(d.get('receptions')),
            safe_float(d.get('receiving_yards')),
            safe_int(d.get('receiving_tds')),
            safe_float(d.get('fantasy_points')),
            safe_float(d.get('fantasy_points_ppr')),
        ))

    sql = """
        INSERT INTO weekly_stats (
            player_id, player_name, season, week, season_type,
            team, opponent, position,
            completions, attempts, passing_yards, passing_tds, interceptions,
            carries, rushing_yards, rushing_tds,
            targets, receptions, receiving_yards, receiving_tds,
            fantasy_points, fantasy_points_ppr
        ) VALUES %s
        ON CONFLICT (player_id, season, week, team) DO NOTHING
    """

    with get_connection() as conn:
        with conn.cursor() as cur:
            execute_values(cur, sql, rows)
        conn.commit()

    print(f"   ✅ {len(rows)} weekly stat rows inserted.")

    
# ── Main ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    # Start with 2023-2024 for testing, add more seasons later
    SEASONS = [2023, 2024]

    ingest_schedules(SEASONS)
    ingest_rosters(SEASONS)
    ingest_weekly_stats(SEASONS)

    print("\n🏈 Ingestion complete.")