# pages/player_lookup.py
# Player Lookup — search a player and see their full season breakdown
# Joins weekly_stats with rosters to show full player names

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

st.title("🔍 Player Lookup")
st.caption("Search for any player and view their weekly performance.")

st.divider()

# ── Search ─────────────────────────────────────────────────────────────────────

search = st.text_input("Search player name", placeholder="e.g. Lamar Jackson, Tyreek Hill, Brian Robinson")

if not search:
    st.info("Enter a player name above to get started.")
    st.stop()

# Join with rosters to get full names, fall back to abbreviated name if no match
players = run_query("""
    SELECT DISTINCT
        w.player_id,
        COALESCE(r.full_name, w.player_name) AS full_name,
        w.player_name                         AS abbrev_name,
        w.position,
        w.team
    FROM weekly_stats w
    LEFT JOIN rosters r
        ON w.player_id = r.player_id
        AND w.season = r.season
    WHERE LOWER(COALESCE(r.full_name, w.player_name)) LIKE LOWER(%s)
    ORDER BY full_name
""", params=(f"%{search}%",))

if players.empty:
    st.warning(f"No players found matching '{search}'.")
    st.stop()

# ── Player selector ────────────────────────────────────────────────────────────

selected_row = st.selectbox(
    "Select player",
    players.itertuples(index=False),
    format_func=lambda r: f"{r.full_name} — {r.position} | {r.team}"
)

selected_id   = selected_row.player_id
selected_name = selected_row.full_name

st.divider()

# ── Season summary ─────────────────────────────────────────────────────────────

st.subheader(f"{selected_name} — Season Summary")

summary = run_query("""
    SELECT
        w.season,
        COUNT(w.week)                                  AS games_played,
        SUM(w.passing_yards)                           AS pass_yds,
        SUM(w.passing_tds)                             AS pass_tds,
        SUM(w.rushing_yards)                           AS rush_yds,
        SUM(w.rushing_tds)                             AS rush_tds,
        SUM(w.receptions)                              AS receptions,
        SUM(w.receiving_yards)                         AS rec_yds,
        SUM(w.receiving_tds)                           AS rec_tds,
        ROUND(SUM(w.fantasy_points_ppr)::numeric, 1)   AS total_ppr,
        ROUND(AVG(w.fantasy_points_ppr)::numeric, 1)   AS avg_ppr_per_game
    FROM weekly_stats w
    WHERE w.player_id = %s
    AND w.season_type = 'REG'
    GROUP BY w.season
    ORDER BY w.season DESC
""", params=(selected_id,))

st.dataframe(summary, use_container_width=True, hide_index=True)

st.divider()

# ── Week by week breakdown ─────────────────────────────────────────────────────

season_filter = st.selectbox("Season", summary["season"].tolist(), index=0)

st.subheader(f"Week by Week — {season_filter}")

weekly = run_query("""
    SELECT
        w.week,
        w.opponent,
        w.completions,
        w.attempts,
        w.passing_yards,
        w.passing_tds,
        w.carries,
        w.rushing_yards,
        w.rushing_tds,
        w.targets,
        w.receptions,
        w.receiving_yards,
        w.receiving_tds,
        ROUND(w.fantasy_points::numeric, 1)     AS fantasy_pts,
        ROUND(w.fantasy_points_ppr::numeric, 1) AS fantasy_pts_ppr
    FROM weekly_stats w
    WHERE w.player_id = %s
    AND w.season = %s
    AND w.season_type = 'REG'
    ORDER BY w.week ASC
""", params=(selected_id, season_filter))

st.dataframe(weekly, use_container_width=True, hide_index=True)

# ── PPR points chart ───────────────────────────────────────────────────────────

st.subheader("PPR Points by Week")
st.bar_chart(weekly.set_index("week")["fantasy_pts_ppr"])