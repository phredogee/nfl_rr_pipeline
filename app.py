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

# Force dark NFL theme via CSS injection
st.markdown("""
    <style>
        .stApp, .main, .block-container,
        [data-testid="stAppViewContainer"],
        [data-testid="stMain"],
        [data-testid="block-container"] {
             background-color: #0E1117 !important;
             color: #FAFAFA !important;
}

        .stApp > header {
            background-color: #0E1117 !important;
}

        [data-testid="stSidebar"] {
            background-color: #1C2333;
        }

        [data-testid="stMetric"] {
            background-color: #1C2333;
            border-radius: 8px;
            padding: 16px;
            border-left: 3px solid #00D4AA;
        }

        [data-testid="stMetricValue"] {
            color: #00D4AA;
            font-size: 2rem;
            font-weight: 700;
        }

        [data-testid="stMetricLabel"] {
            color: #FAFAFA;
            font-size: 0.9rem;
        }

        [data-testid="stDataFrame"] {
            background-color: #1C2333;
            border-radius: 8px;
        }

        .stButton > button {
            background-color: #00D4AA;
            color: #0E1117;
            border: none;
            border-radius: 6px;
            font-weight: 600;
        }

        .stButton > button:hover {
            background-color: #00B894;
            color: #0E1117;
        }

        .stTextInput > div > div > input,
        .stSelectbox > div > div,
        .stNumberInput > div > div > input {
            background-color: #1C2333;
            color: #FAFAFA;
            border-color: #2D3748;
        }

        .streamlit-expanderHeader {
            background-color: #1C2333;
            border-radius: 6px;
        }

        hr {
            border-color: #2D3748;
        }

        h1, h2, h3 {
            color: #FAFAFA;
        }

        .stCaption {
            color: #A0AEC0;
        }

        [data-testid="stSidebarNav"] a {
            color: #FAFAFA;
        }

        [data-testid="stSidebarNav"] a:hover {
            color: #00D4AA;
            background-color: #2D3748;
        }
    </style>
""", unsafe_allow_html=True)

# Navigation
pg = st.navigation([
    st.Page("pages/dashboard.py",       title="Pipeline Dashboard", icon="📊"),
    st.Page("pages/stats_explorer.py",  title="Stats Explorer",     icon="📈"),
    st.Page("pages/player_lookup.py",   title="Player Lookup",      icon="🔍"),
    st.Page("pages/matchup_compare.py", title="Matchup Comparison", icon="⚔️"),
    st.Page("pages/league_manager.py",  title="League Manager",     icon="🏆"),
])

pg.run()