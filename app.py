import streamlit as st
import pandas as pd
import numpy as np
from scipy.stats import poisson
import requests

st.set_page_config(
    page_title="AI Football Intelligence",
    layout="wide"
)

st.title("⚽ AI Football Intelligence")

############################################
# CONFIG
############################################

API_TOKEN = "PUT_YOUR_TOKEN_HERE"

LEAGUES = {
    "Premier League": "E0 (2).csv",
    "Championship": "E1.csv",
    "La Liga": "SP1.csv",
    "Serie A": "I1.csv",
    "Bundesliga": "D1.csv",
    "Greece": "G1.csv"
}

############################################
# SIDEBAR
############################################

st.sidebar.title("⚙️ Controls")

league = st.sidebar.selectbox(
    "League",
    list(LEAGUES.keys())
)

data = pd.read_csv(LEAGUES[league])

teams = sorted(data["HomeTeam"].unique())

home_team = st.sidebar.selectbox("Home Team", teams)
away_team = st.sidebar.selectbox("Away Team", teams)

predict_button = st.sidebar.button("Predict Match")

############################################
# MODEL
############################################

league_home_goals = data["FTHG"].mean()
league_away_goals = data["FTAG"].mean()

home_attack = data.groupby("HomeTeam")["FTHG"].mean() / league_home_goals
away_attack = data.groupby("AwayTeam")["FTAG"].mean() / league_away_goals

home_defense = data.groupby("HomeTeam")["FTAG"].mean() / league_away_goals
away_defense = data.groupby("AwayTeam")["FTHG"].mean() / league_home_goals

############################################
# TABS
############################################

tab1, tab2, tab3 = st.tabs([
    "📅 Matches Today",
    "🧠 AI Prediction",
    "💰 Value Bets"
])

############################################
# MATCHES TODAY
############################################

with tab1:

    st.header("Today's Matches")

    url = f"https://api.sportmonks.com/v3/football/fixtures/date/2026-03-26?api_token={API_TOKEN}&include=participants"

    response = requests.get(url)
    json_data = response.json()

    if "data" not in json_data:

        st.error("API connection problem")
        st.write(json_data)

    else:

        matches = json_data["data"]

        for match in matches:

            teams = match.get("participants", [])

            if len(teams) >= 2:

                home = teams[0]["name"]
                away = teams[1]["name"]

                time = match["starting_at"]

                col1, col2, col3 = st.columns([4,1,4])

                with col1:
                    st.markdown(f"### {home}")

                with col2:
                    st.markdown("### vs")

                with col3:
                    st.markdown(f"### {away}")

                st.caption(time)

                st.divider()

############################################
# AI PREDICTION
############################################

with tab2:

    if predict_button:

        home_xg = home_attack[home_team] * away_defense[away_team] * league_home_goals
        away_xg = away_attack[away_team] * home_defense[home_team] * league_away_goals

        max_goals = 6

        home_probs = [poisson.pmf(i, home_xg) for i in range(max_goals)]
        away_probs = [poisson.pmf(i, away_xg) for i in range(max_goals)]

        home_win = 0
        draw = 0
        away_win = 0

        for i in range(max_goals):
            for j in range(max_goals):

                prob = home_probs[i] * away_probs[j]

                if i > j:
                    home_win += prob
                elif i == j:
                    draw += prob
                else:
                    away_win += prob

        c1, c2, c3 = st.columns(3)

        c1.metric("Home Win", f"{round(home_win*100,2)}%")
        c2.metric("Draw", f"{round(draw*100,2)}%")
        c3.metric("Away Win", f"{round(away_win*100,2)}%")

        st.subheader("Expected Goals")

        st.write(home_team, round(home_xg,2))
        st.write(away_team, round(away_xg,2))

############################################
# VALUE BETS
############################################

with tab3:

    st.header("Value Bet Scanner")

    odds = st.number_input("Bookmaker odds", value=2.20)

    home_xg = home_attack[home_team] * away_defense[away_team] * league_home_goals
    away_xg = away_attack[away_team] * home_defense[home_team] * league_away_goals

    model_prob = home_xg / (home_xg + away_xg)

    implied_prob = 1 / odds

    edge = model_prob - implied_prob

    if edge > 0.05:

        st.success("🔥 VALUE BET FOUND")

        st.write("Match:", home_team, "vs", away_team)

        st.write("Model probability:", round(model_prob*100,2), "%")

        st.write("Odds:", odds)

        st.write("Edge:", round(edge*100,2), "%")

    else:

        st.info("No value bet detected")
