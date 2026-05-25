# pages/league_manager.py
# League Manager — create and manage fantasy league profiles
# Includes full custom scoring configuration per league

import streamlit as st
import json
import os

LEAGUES_FILE = os.path.join(os.path.dirname(__file__), '..', 'config', 'leagues.json')

# ── Default scoring config ─────────────────────────────────────────────────────

DEFAULT_SCORING = {
    "passing": {
        "yards_per_point":          25.0,
        "td_points":                 4.0,
        "int_deduction":            -2.0,
        "sack_yard_deduction":       0.0,
        "sack_fumble_lost":         -2.0,
        "two_pt_conversion":         2.0,
        "completion_bonus":          0.0,
        "incomplete_deduction":      0.0,
        "bonus_300_yards":           0.0,
        "bonus_400_yards":           0.0,
    },
    "rushing": {
        "yards_per_point":          10.0,
        "td_points":                 6.0,
        "fumble_lost_deduction":    -2.0,
        "two_pt_conversion":         2.0,
        "bonus_100_yards":           0.0,
        "bonus_200_yards":           0.0,
    },
    "receiving": {
        "yards_per_point":          10.0,
        "td_points":                 6.0,
        "reception_bonus":           0.5,
        "fumble_lost_deduction":    -2.0,
        "two_pt_conversion":         2.0,
        "bonus_100_yards":           0.0,
        "bonus_200_yards":           0.0,
    },
    "kicking": {
        "pat_made":                  1.0,
        "pat_missed":               -1.0,
        "fg_made_0_39":              3.0,
        "fg_made_40_49":             4.0,
        "fg_made_50_plus":           5.0,
        "fg_missed_0_39":           -1.0,
        "fg_missed_40_49":           0.0,
        "fg_missed_50_plus":         0.0,
    },
    "dst": {
        "sack":                      1.0,
        "interception":              2.0,
        "fumble_recovered":          2.0,
        "touchdown":                 6.0,
        "safety":                    2.0,
        "blocked_kick":              2.0,
        "return_td":                 6.0,
        "three_and_out":             0.0,
        "fourth_down_stop":          0.0,
        "points_allowed_0":         10.0,
        "points_allowed_1_6":        7.0,
        "points_allowed_7_13":       4.0,
        "points_allowed_14_20":      1.0,
        "points_allowed_21_27":      0.0,
        "points_allowed_28_34":     -1.0,
        "points_allowed_35_plus":   -4.0,
        "yards_allowed_0_99":        5.0,
        "yards_allowed_100_199":     3.0,
        "yards_allowed_200_299":     2.0,
        "yards_allowed_300_399":     0.0,
        "yards_allowed_400_449":    -1.0,
        "yards_allowed_450_499":    -3.0,
        "yards_allowed_500_plus":   -5.0,
    }
}

# ── Labels for display ─────────────────────────────────────────────────────────
# Maps config key → human readable label + whether it's available now or [LIVE API]

SCORING_LABELS = {
    "passing": {
        "yards_per_point":          ("Yards per point",              True),
        "td_points":                ("TD points",                     True),
        "int_deduction":            ("INT deduction",                 True),
        "sack_yard_deduction":      ("Sack yard deduction (per yd)",  True),
        "sack_fumble_lost":         ("Sack fumble lost deduction",    True),
        "two_pt_conversion":        ("2PT conversion bonus",          True),
        "completion_bonus":         ("Completion bonus",              True),
        "incomplete_deduction":     ("Incomplete pass deduction",     True),
        "bonus_300_yards":          ("300+ yard game bonus",          True),
        "bonus_400_yards":          ("400+ yard game bonus",          True),
    },
    "rushing": {
        "yards_per_point":          ("Yards per point",              True),
        "td_points":                ("TD points",                     True),
        "fumble_lost_deduction":    ("Fumble lost deduction",         True),
        "two_pt_conversion":        ("2PT conversion bonus",          True),
        "bonus_100_yards":          ("100+ yard game bonus",          True),
        "bonus_200_yards":          ("200+ yard game bonus",          True),
    },
    "receiving": {
        "yards_per_point":          ("Yards per point",              True),
        "td_points":                ("TD points",                     True),
        "reception_bonus":          ("Reception bonus (PPR)",         True),
        "fumble_lost_deduction":    ("Fumble lost deduction",         True),
        "two_pt_conversion":        ("2PT conversion bonus",          True),
        "bonus_100_yards":          ("100+ yard game bonus",          True),
        "bonus_200_yards":          ("200+ yard game bonus",          True),
    },
    "kicking": {
        "pat_made":                 ("PAT made",                      False),
        "pat_missed":               ("PAT missed",                    False),
        "fg_made_0_39":             ("FG made 0-39 yds",              False),
        "fg_made_40_49":            ("FG made 40-49 yds",             False),
        "fg_made_50_plus":          ("FG made 50+ yds",               False),
        "fg_missed_0_39":           ("FG missed 0-39 yds",            False),
        "fg_missed_40_49":          ("FG missed 40-49 yds",           False),
        "fg_missed_50_plus":        ("FG missed 50+ yds",             False),
    },
    "dst": {
        "sack":                     ("Sack",                          False),
        "interception":             ("Interception",                  False),
        "fumble_recovered":         ("Fumble recovered",              False),
        "touchdown":                ("Touchdown",                     False),
        "safety":                   ("Safety",                        False),
        "blocked_kick":             ("Blocked kick",                  False),
        "return_td":                ("Return TD",                     False),
        "three_and_out":            ("3-and-out forced",              False),
        "fourth_down_stop":         ("4th down stop",                 False),
        "points_allowed_0":         ("Points allowed: 0",             False),
        "points_allowed_1_6":       ("Points allowed: 1-6",           False),
        "points_allowed_7_13":      ("Points allowed: 7-13",          False),
        "points_allowed_14_20":     ("Points allowed: 14-20",         False),
        "points_allowed_21_27":     ("Points allowed: 21-27",         False),
        "points_allowed_28_34":     ("Points allowed: 28-34",         False),
        "points_allowed_35_plus":   ("Points allowed: 35+",           False),
        "yards_allowed_0_99":       ("Yards allowed: 0-99",           False),
        "yards_allowed_100_199":    ("Yards allowed: 100-199",        False),
        "yards_allowed_200_299":    ("Yards allowed: 200-299",        False),
        "yards_allowed_300_399":    ("Yards allowed: 300-399",        False),
        "yards_allowed_400_449":    ("Yards allowed: 400-449",        False),
        "yards_allowed_450_499":    ("Yards allowed: 450-499",        False),
        "yards_allowed_500_plus":   ("Yards allowed: 500+",           False),
    }
}

SLOT_ELIGIBILITY = {
    "QB":        ["QB"],
    "RB":        ["RB"],
    "WR":        ["WR"],
    "TE":        ["TE"],
    "FLEX":      ["RB", "WR", "TE"],
    "SuperFlex": ["QB", "RB", "WR", "TE"],
    "K":         ["K"],
    "DST":       ["DST"],
}

POSITION_SLOTS = list(SLOT_ELIGIBILITY.keys())

# ── Helpers ────────────────────────────────────────────────────────────────────

def load_leagues() -> dict:
    if not os.path.exists(LEAGUES_FILE):
        return {}
    with open(LEAGUES_FILE, 'r') as f:
        return json.load(f)

def save_leagues(leagues: dict):
    with open(LEAGUES_FILE, 'w') as f:
        json.dump(leagues, f, indent=2)

def scoring_section(category: str, current: dict) -> dict:
    """
    Render scoring inputs for one category (passing, rushing, etc).
    Returns updated dict of values.
    """
    labels = SCORING_LABELS[category]
    defaults = DEFAULT_SCORING[category]
    updated = {}

    col1, col2 = st.columns(2)
    for i, (key, (label, available)) in enumerate(labels.items()):
        default_val = current.get(key, defaults.get(key, 0.0))
        display_label = label if available else f"{label} 🔒 Live API"

        with col1 if i % 2 == 0 else col2:
            updated[key] = st.number_input(
                display_label,
                value=float(default_val),
                step=0.5,
                format="%.1f",
                key=f"scoring_{category}_{key}",
                disabled=not available,   # grey out Live API fields
                help="Available with live API integration" if not available else None
            )

    return updated

# ── Page ───────────────────────────────────────────────────────────────────────

st.title("🏆 League Manager")
st.caption("Create and manage your fantasy league roster configurations and scoring settings.")

st.divider()

leagues = load_leagues()

# ── Existing leagues ───────────────────────────────────────────────────────────

if leagues:
    st.subheader("Your Leagues")

    for league_name, config in list(leagues.items()):
        with st.expander(f"📋 {league_name}"):
            st.write("**Roster slots:**")
            slot_summary = [f"{count}x {slot}" for slot, count in config["slots"].items() if count > 0]
            st.write(", ".join(slot_summary))

            st.write("**Scoring format:**", config.get("scoring", "Custom"))

            if st.button(f"Delete {league_name}", key=f"delete_{league_name}", type="secondary"):
                del leagues[league_name]
                save_leagues(leagues)
                st.success(f"Deleted '{league_name}'.")
                st.rerun()

st.divider()

# ── Create new league ──────────────────────────────────────────────────────────

st.subheader("Create New League")

league_name = st.text_input("League name", placeholder="e.g. ESPN 10-Team Half PPR")

if league_name:

    st.markdown("### 📋 Roster Slots")
    st.caption("Set how many of each position your league starts.")

    col1, col2 = st.columns(2)
    slot_counts = {}
    defaults_slots = {
        "QB": 1, "RB": 2, "WR": 2, "TE": 1,
        "FLEX": 1, "SuperFlex": 0, "K": 1, "DST": 1
    }
    for i, slot in enumerate(POSITION_SLOTS):
        with col1 if i % 2 == 0 else col2:
            slot_counts[slot] = st.number_input(
                slot,
                min_value=0, max_value=5,
                value=defaults_slots.get(slot, 0),
                step=1,
                key=f"slot_{slot}"
            )

    st.divider()

    # ── Scoring config ─────────────────────────────────────────────────────────

    st.markdown("### 🏈 Passing Scoring")
    passing_scoring = scoring_section("passing", DEFAULT_SCORING["passing"])

    st.markdown("### 🏃 Rushing Scoring")
    rushing_scoring = scoring_section("rushing", DEFAULT_SCORING["rushing"])

    st.markdown("### 🙌 Receiving Scoring")
    receiving_scoring = scoring_section("receiving", DEFAULT_SCORING["receiving"])

    st.markdown("### 🦵 Kicking Scoring")
    st.caption("🔒 Kicking stats require live API integration — values saved for future use.")
    kicking_scoring = scoring_section("kicking", DEFAULT_SCORING["kicking"])

    st.markdown("### 🛡️ DST Scoring")
    st.caption("🔒 DST stats require live API integration — values saved for future use.")
    dst_scoring = scoring_section("dst", DEFAULT_SCORING["dst"])

    st.divider()

    if st.button("💾 Save League", type="primary"):
        if league_name in leagues:
            st.error(f"A league named '{league_name}' already exists.")
        elif sum(slot_counts.values()) == 0:
            st.error("Please add at least one roster slot.")
        else:
            leagues[league_name] = {
                "scoring":          "Custom",
                "slots":            slot_counts,
                "slot_eligibility": SLOT_ELIGIBILITY,
                "scoring_config": {
                    "passing":   passing_scoring,
                    "rushing":   rushing_scoring,
                    "receiving": receiving_scoring,
                    "kicking":   kicking_scoring,
                    "dst":       dst_scoring,
                }
            }
            save_leagues(leagues)
            st.success(f"League '{league_name}' saved!")
            st.rerun()