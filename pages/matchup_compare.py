# pages/matchup_compare.py
# Matchup Comparison — compare your lineup vs opponent's projected points
# Uses saved league profiles from League Manager for roster configuration

import streamlit as st
import psycopg2
import pandas as pd
import json
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'config'))
from db_config import DB_CONFIG

LEAGUES_FILE = os.path.join(os.path.dirname(__file__), '..', 'config', 'leagues.json')

# ── Connection helper ──────────────────────────────────────────────────────────

@st.cache_resource
def get_connection():
    return psycopg2.connect(**DB_CONFIG)

def run_query(sql: str, params=None) -> pd.DataFrame:
    conn = get_connection()
    return pd.read_sql(sql, conn, params=params)

# ── League loader ──────────────────────────────────────────────────────────────

def load_leagues() -> dict:
    if not os.path.exists(LEAGUES_FILE):
        return {}
    with open(LEAGUES_FILE, 'r') as f:
        return json.load(f)

# ── Player data ────────────────────────────────────────────────────────────────

@st.cache_data
def get_all_players(season: int, scoring_column: str) -> pd.DataFrame:
    """Load all players with full names and avg points for the selected season."""
    return run_query(f"""
        SELECT
            w.player_id,
            COALESCE(MAX(r.full_name), MAX(w.player_name)) AS full_name,
            MAX(w.position)                                 AS position,
            MAX(w.team)                                     AS team,
            ROUND(AVG(w.{scoring_column})::numeric, 1)      AS avg_pts
        FROM weekly_stats w
        LEFT JOIN rosters r
            ON w.player_id = r.player_id
            AND w.season = r.season
        WHERE w.season = %s
        AND w.season_type = 'REG'
        GROUP BY w.player_id
        ORDER BY avg_pts DESC NULLS LAST
    """, params=(season,))

# ── Player selector ────────────────────────────────────────────────────────────

def player_selector(label: str, players_df: pd.DataFrame, key: str, positions: list[str]):
    """Single searchable dropdown filtered to eligible positions for this slot."""
    filtered = players_df[players_df["position"].isin(positions)]
    options  = [None] + list(filtered.itertuples(index=False))

    return st.selectbox(
        label,
        options,
        format_func=lambda r: "— select a player —" if r is None
            else f"{r.full_name} — {r.position} | {r.team} | avg {r.avg_pts} pts",
        key=f"select_{key}"
    )

# ── Lineup builder ─────────────────────────────────────────────────────────────

def build_lineup(side: str, players_df: pd.DataFrame, slot_config: dict, eligibility: dict) -> pd.DataFrame:
    """
    Dynamically build lineup slots based on league config.
    slot_config: {"QB": 1, "RB": 2, ...}
    eligibility: {"QB": ["QB"], "FLEX": ["RB","WR","TE"], ...}
    """
    rows = []
    counter = 0

    for slot, count in slot_config.items():
        if count == 0:
            continue
        for n in range(count):
            # Label slot with number if more than one (e.g. RB1, RB2)
            label = f"{slot}{n+1}" if count > 1 else slot
            eligible_positions = eligibility.get(slot, [slot])
            player = player_selector(label, players_df, key=f"{side}_{counter}", positions=eligible_positions)
            rows.append({
                "slot":    label,
                "player":  player.full_name if player else "— empty —",
                "position": player.position if player else "",
                "team":    player.team if player else "",
                "avg_pts": float(player.avg_pts) if player and player.avg_pts else 0.0
            })
            counter += 1

    return pd.DataFrame(rows)

# ── Page ───────────────────────────────────────────────────────────────────────

st.title("⚔️ Matchup Comparison")
st.caption("Compare your starting lineup vs your opponent's projected points.")

st.divider()

# ── League selector ────────────────────────────────────────────────────────────

leagues = load_leagues()

if not leagues:
    st.warning("No leagues saved yet. Go to League Manager to create one first.")
    st.stop()

league_name = st.selectbox("Select League", list(leagues.keys()))
league      = leagues[league_name]
scoring     = league["scoring"]
scoring_col = league["scoring_column"]
slot_config = league["slots"]
eligibility = league["slot_eligibility"]

st.caption(f"Scoring: {scoring}")

# ── Optional slot override for this matchup ────────────────────────────────────

with st.expander("⚙️ Adjust slots for this matchup (optional)"):
    st.caption("Override your league's default roster slots for this week only.")
    col1, col2 = st.columns(2)
    adjusted_slots = {}
    for i, (slot, default_count) in enumerate(slot_config.items()):
        with col1 if i % 2 == 0 else col2:
            adjusted_slots[slot] = st.number_input(
                slot,
                min_value=0,
                max_value=5,
                value=default_count,  # starts at league default
                step=1,
                key=f"override_{slot}"
            )

# Use adjusted slots if any were changed, otherwise use league defaults
slot_config = adjusted_slots

st.divider()

# ── Season selector ────────────────────────────────────────────────────────────

season     = st.selectbox("Season", [2024, 2023], index=0)
players_df = get_all_players(season, scoring_col)

st.divider()

# ── Lineups ────────────────────────────────────────────────────────────────────

col_mine, col_opp = st.columns(2)

with col_mine:
    st.subheader("🟦 My Lineup")
    my_lineup = build_lineup("mine", players_df, slot_config, eligibility)

with col_opp:
    st.subheader("🟥 Opponent's Lineup")
    opp_lineup = build_lineup("opp", players_df, slot_config, eligibility)

st.divider()

# ── Projected totals ───────────────────────────────────────────────────────────

st.subheader("📊 Projected Score Comparison")

my_total  = my_lineup["avg_pts"].sum()
opp_total = opp_lineup["avg_pts"].sum()

col1, col2, col3 = st.columns(3)
col1.metric("🟦 My Projected Total",       f"{my_total:.1f} pts")
col2.metric("🟥 Opponent Projected Total", f"{opp_total:.1f} pts")

diff = my_total - opp_total
if diff > 0:
    col3.metric("Projected Margin", f"+{diff:.1f}", delta=f"You win by {diff:.1f}")
elif diff < 0:
    col3.metric("Projected Margin", f"{diff:.1f}", delta=f"You lose by {abs(diff):.1f}", delta_color="inverse")
else:
    col3.metric("Projected Margin", "0.0", delta="Projected tie")

st.divider()

# ── Side by side breakdown ─────────────────────────────────────────────────────

st.subheader("Lineup Breakdown")

combined = pd.DataFrame({
    "Slot":        my_lineup["slot"],
    "My Player":   my_lineup["player"],
    "My Avg Pts":  my_lineup["avg_pts"],
    "Opp Player":  opp_lineup["player"],
    "Opp Avg Pts": opp_lineup["avg_pts"],
})

st.dataframe(combined, use_container_width=True, hide_index=True)