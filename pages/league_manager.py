# pages/league_manager.py
# League Manager — create and manage fantasy league profiles
# Saves league configs to config/leagues.json

import streamlit as st
import json
import os

LEAGUES_FILE = os.path.join(os.path.dirname(__file__), '..', 'config', 'leagues.json')

# ── Persistence helpers ────────────────────────────────────────────────────────

def load_leagues() -> dict:
    """Load leagues from JSON file, return empty dict if file doesn't exist."""
    if not os.path.exists(LEAGUES_FILE):
        return {}
    with open(LEAGUES_FILE, 'r') as f:
        return json.load(f)

def save_leagues(leagues: dict):
    """Save leagues dict to JSON file."""
    with open(LEAGUES_FILE, 'w') as f:
        json.dump(leagues, f, indent=2)

# ── Scoring options ────────────────────────────────────────────────────────────

SCORING_OPTIONS = {
    "Half PPR": "fantasy_points_ppr",  # we'll average half and standard
    "Full PPR": "fantasy_points_ppr",
    "Standard": "fantasy_points",
}

# Position slots available to configure
POSITION_SLOTS = ["QB", "RB", "WR", "TE", "FLEX", "SuperFlex", "K", "DST"]

# Which positions are eligible per slot
SLOT_ELIGIBILITY = {
    "QB":       ["QB"],
    "RB":       ["RB"],
    "WR":       ["WR"],
    "TE":       ["TE"],
    "FLEX":     ["RB", "WR", "TE"],
    "SuperFlex":["QB", "RB", "WR", "TE"],
    "K":        ["K"],
    "DST":      ["DST"],
}

# ── Page ───────────────────────────────────────────────────────────────────────

st.title("🏆 League Manager")
st.caption("Create and manage your fantasy league roster configurations.")

st.divider()

leagues = load_leagues()

# ── Existing leagues ───────────────────────────────────────────────────────────

if leagues:
    st.subheader("Your Leagues")

    for league_name, config in leagues.items():
        with st.expander(f"📋 {league_name} — {config['scoring']}"):
            st.write("**Roster slots:**")

            # Display current slot counts
            slot_summary = []
            for slot, count in config["slots"].items():
                if count > 0:
                    slot_summary.append(f"{count}x {slot}")
            st.write(", ".join(slot_summary))

            if st.button(f"Delete {league_name}", key=f"delete_{league_name}", type="secondary"):
                del leagues[league_name]
                save_leagues(leagues)
                st.success(f"Deleted '{league_name}'.")
                st.rerun()
else:
    st.info("No leagues saved yet. Create one below.")

st.divider()

# ── Create new league ──────────────────────────────────────────────────────────

st.subheader("Create New League")

with st.form("new_league_form"):
    league_name = st.text_input("League name", placeholder="e.g. ESPN 10-Team Half PPR")
    scoring     = st.selectbox("Scoring format", list(SCORING_OPTIONS.keys()), index=0)

    st.markdown("**Roster slots** — set how many of each position:")

    # Two columns for slot counters to keep it compact
    col1, col2 = st.columns(2)
    slot_counts = {}

    for i, slot in enumerate(POSITION_SLOTS):
        # Default counts for a standard lineup
        defaults = {
            "QB": 1, "RB": 2, "WR": 2, "TE": 1,
            "FLEX": 1, "SuperFlex": 0, "K": 1, "DST": 1
        }
        with col1 if i % 2 == 0 else col2:
            slot_counts[slot] = st.number_input(
                slot,
                min_value=0,
                max_value=5,
                value=defaults.get(slot, 0),
                step=1,
                key=f"slot_{slot}"
            )

    submitted = st.form_submit_button("Save League", type="primary")

    if submitted:
        if not league_name.strip():
            st.error("Please enter a league name.")
        elif league_name in leagues:
            st.error(f"A league named '{league_name}' already exists.")
        elif sum(slot_counts.values()) == 0:
            st.error("Please add at least one roster slot.")
        else:
            leagues[league_name] = {
                "scoring":          scoring,
                "scoring_column":   SCORING_OPTIONS[scoring],
                "slots":            slot_counts,
                "slot_eligibility": SLOT_ELIGIBILITY,
            }
            save_leagues(leagues)
            st.success(f"League '{league_name}' saved!")
            st.rerun()