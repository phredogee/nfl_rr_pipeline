# app.py
# Main entry point for the NFL RR Pipeline Streamlit app
# Run with: streamlit run app.py

import streamlit as st

st.set_page_config(
    page_title="NFL RR Pipeline",
    page_icon="🏈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Navigation
pg = st.navigation([
    st.Page("pages/dashboard.py",        title="Pipeline Dashboard", icon="📊"),
    st.Page("pages/stats_explorer.py",   title="Stats Explorer",     icon="📈"),
    st.Page("pages/player_lookup.py",    title="Player Lookup",      icon="🔍"),
    st.Page("pages/matchup_compare.py",  title="Matchup Comparison", icon="⚔️"),
    st.Page("pages/league_manager.py",   title="League Manager",     icon="🏆"),
])

pg.run()