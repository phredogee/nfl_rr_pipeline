# pages/dashboard.py
# Pipeline Dashboard — shows database health, row counts, and sanity sweep results

import streamlit as st
import psycopg2
import pandas as pd
import sys
import os
from datetime import datetime

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'config'))
from db_config import DB_CONFIG

# ── Connection helper ──────────────────────────────────────────────────────────

@st.cache_resource
def get_connection():
    """Cache the DB connection so we don't reconnect on every rerender."""
    return psycopg2.connect(**DB_CONFIG)

def run_query(sql: str) -> pd.DataFrame:
    """Run a SQL query and return a DataFrame."""
    conn = get_connection()
    return pd.read_sql(sql, conn)

# ── Page ───────────────────────────────────────────────────────────────────────

st.title("📊 Pipeline Dashboard")
st.caption(f"Last refreshed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

st.divider()

# ── Row counts ─────────────────────────────────────────────────────────────────

st.subheader("Database Overview")

counts = run_query("""
    SELECT 'schedules'    AS table_name, COUNT(*) AS row_count FROM schedules
    UNION ALL
    SELECT 'rosters',                    COUNT(*)              FROM rosters
    UNION ALL
    SELECT 'weekly_stats',               COUNT(*)              FROM weekly_stats
""")

col1, col2, col3 = st.columns(3)
col1.metric("📅 Schedules",    f"{counts.loc[0, 'row_count']:,}")
col2.metric("👥 Rosters",      f"{counts.loc[1, 'row_count']:,}")
col3.metric("📈 Weekly Stats", f"{counts.loc[2, 'row_count']:,}")

st.divider()

# ── Season coverage ────────────────────────────────────────────────────────────

st.subheader("Season Coverage")

coverage = run_query("""
    SELECT 'schedules' AS table_name, season, COUNT(*) AS rows
    FROM schedules GROUP BY season
    UNION ALL
    SELECT 'rosters', season, COUNT(*)
    FROM rosters GROUP BY season
    UNION ALL
    SELECT 'weekly_stats', season, COUNT(*)
    FROM weekly_stats GROUP BY season
    ORDER BY table_name, season
""")

st.dataframe(coverage, use_container_width=True, hide_index=True)

st.divider()

# ── Null check ─────────────────────────────────────────────────────────────────

st.subheader("Data Quality — Null Check")

nulls = run_query("""
    SELECT 'schedules.game_id'       AS column_name, COUNT(*) AS null_count FROM schedules    WHERE game_id IS NULL
    UNION ALL
    SELECT 'schedules.home_team',                    COUNT(*) FROM schedules    WHERE home_team IS NULL
    UNION ALL
    SELECT 'schedules.away_team',                    COUNT(*) FROM schedules    WHERE away_team IS NULL
    UNION ALL
    SELECT 'rosters.player_id',                      COUNT(*) FROM rosters      WHERE player_id IS NULL
    UNION ALL
    SELECT 'rosters.team',                           COUNT(*) FROM rosters      WHERE team IS NULL
    UNION ALL
    SELECT 'weekly_stats.player_id',                 COUNT(*) FROM weekly_stats WHERE player_id IS NULL
    UNION ALL
    SELECT 'weekly_stats.season',                    COUNT(*) FROM weekly_stats WHERE season IS NULL
    UNION ALL
    SELECT 'weekly_stats.week',                      COUNT(*) FROM weekly_stats WHERE week IS NULL
""")

# Color code: green if zero nulls, red if any found
def highlight_nulls(val):
    return 'color: green' if val == 0 else 'color: red'

st.dataframe(
    nulls.style.map(highlight_nulls, subset=['null_count']),
    use_container_width=True,
    hide_index=True
)

st.divider()

# ── Week range ─────────────────────────────────────────────────────────────────

st.subheader("Week Range by Season")

weeks = run_query("""
    SELECT
        season,
        MIN(week) AS min_week,
        MAX(week) AS max_week,
        COUNT(DISTINCT week) AS distinct_weeks
    FROM weekly_stats
    WHERE season_type = 'REG'
    GROUP BY season
    ORDER BY season
""")

st.dataframe(weeks, use_container_width=True, hide_index=True)

st.divider()

# ── Top fantasy scorers ────────────────────────────────────────────────────────

st.subheader("Top 10 PPR Scorers (All Time)")

top = run_query("""
    SELECT
        player_name,
        season,
        ROUND(SUM(fantasy_points_ppr)::numeric, 1) AS total_ppr_points
    FROM weekly_stats
    WHERE season_type = 'REG'
    GROUP BY player_name, season
    ORDER BY total_ppr_points DESC
    LIMIT 10
""")

st.dataframe(top, use_container_width=True, hide_index=True)