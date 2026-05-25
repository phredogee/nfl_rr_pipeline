# pages/stats_explorer.py
# Stats Explorer — filter weekly stats by season, week, team, and position

import streamlit as st
import psycopg2
import pandas as pd
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'config'))
from db_config import DB_CONFIG

# ── Connection helper ──────────────────────────────────────────────────────────

@st.cache_resource
def get_connection():
    return psycopg2.connect(**DB_CONFIG)

def run_query(sql: str, params=None) -> pd.DataFrame:
    conn = get_connection()
    return pd.read_sql(sql, conn, params=params)

# ── Page ───────────────────────────────────────────────────────────────────────

st.title("📈 Stats Explorer")
st.caption("Filter and explore weekly player stats across seasons.")

st.divider()

# ── Filters ────────────────────────────────────────────────────────────────────

col1, col2, col3, col4 = st.columns(4)

with col1:
    season = st.selectbox("Season", [2024, 2023], index=0)

with col2:
    week_options = ["All"] + list(range(1, 19))
    week = st.selectbox("Week", week_options, index=0)

with col3:
    teams = run_query("SELECT DISTINCT team FROM weekly_stats ORDER BY team")
    team_options = ["All"] + teams["team"].tolist()
    team = st.selectbox("Team", team_options, index=0)

with col4:
    positions = ["All", "QB", "RB", "WR", "TE", "K"]
    position = st.selectbox("Position", positions, index=0)

st.divider()

# ── Build query dynamically based on filters ───────────────────────────────────

# Why dynamic: we only apply WHERE clauses for filters the user actually set
query = """
    SELECT
        player_name,
        position,
        team,
        season,
        week,
        completions,
        attempts,
        passing_yards,
        passing_tds,
        carries,
        rushing_yards,
        rushing_tds,
        targets,
        receptions,
        receiving_yards,
        receiving_tds,
        ROUND(fantasy_points::numeric, 1)     AS fantasy_pts,
        ROUND(fantasy_points_ppr::numeric, 1) AS fantasy_pts_ppr
    FROM weekly_stats
    WHERE season_type = 'REG'
"""

params = []

query += " AND season = %s"
params.append(season)

if week != "All":
    query += " AND week = %s"
    params.append(week)

if team != "All":
    query += " AND team = %s"
    params.append(team)

if position != "All":
    query += " AND position = %s"
    params.append(position)

query += " ORDER BY fantasy_pts_ppr DESC NULLS LAST"

# ── Results ────────────────────────────────────────────────────────────────────

df = run_query(query, params=tuple(params))

st.subheader(f"Results — {len(df)} players")
st.dataframe(df, use_container_width=True, hide_index=True)
