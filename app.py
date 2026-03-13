import streamlit as st
import pandas as pd
import numpy as np
from scipy.stats import poisson
import requests

st.set_page_config(page_title="AI Football Predictor", layout="wide")

st.title("⚽ AI Football Predictor")

###################################
# LEAGUE FILES
###################################

league_files = {
    "Premier League": "E0 (2).csv",
    "Championship": "E1.csv",
    "La Liga": "SP1.csv",
    "Serie A": "I1.csv",
    "Bundesliga": "D1.csv",
    "Greece": "G1.csv"
}

league = st.sidebar.selectbox("League", list(league_files.keys()))

data = pd.read_csv(league_files[league])

###################################
# MODEL
###################################

league_home_goals = data["FTHG"].mean()
league_away_goals = data["FTAG"].mean()

home_attack = data.groupby("HomeTeam")["FTHG"].mean() / league_home_goals
away_attack = data.groupby("AwayTeam")["FTAG"].mean() / league_away_goals

home_defense = data.groupby("HomeTeam")["FTAG"].mean() / league_away_goals
away_defense = data.groupby("AwayTeam")["FTHG"].mean() / league_home_goals

teams = sorted(data["HomeTeam"].unique())

home_team = st.sidebar.selectbox("Home Team", teams)
away_team = st.sidebar.selectbox("Away Team", teams)

###################################
# TABS
###################################

tab1, tab2, tab3 = st.tabs(["📅 Matches Today", "🧠 AI Prediction", "💰 Value Bets"])

###################################
# AI PREDICTION
###################################

with tab2:

    if st.sidebar.button("Predict Match"):

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

        col1, col2, col3 = st.columns(3)

        col1.metric("Home Win", f"{round(home_win*100,2)}%")
        col2.metric("Draw", f"{round(draw*100,2)}%")
        col3.metric("Away Win", f"{round(away_win*100,2)}%")

        st.subheader("Expected Goals")

        st.write(home_team, round(home_xg,2))
        st.write(away_team, round(away_xg,2))

###################################
# MATCHES TODAY (SPORTMONKS)
###################################

with tab1:

    st.header("Today's Matches")

    API_TOKEN = "5UyoUThTMPItCW81lTazLAgh3PM8QbHEjbXKBOcgBdrvBc4RSEvfhlGDUer6"

    url = f"https://api.sportmonks.com/v3/football/fixtures/date/2026-03-26?api_token={API_TOKEN}&include=participants"

    response = requests.get(url)

    json_data = response.json()

    if "data" not in json_data:

        st.error("API error")
        st.write(json_data)

    else:

        matches = json_data["data"]

        for match in matches:

            teams = match["participants"]

            if len(teams) >= 2:

                home = teams[0]["name"]
                away = teams[1]["name"]
                time = match["starting_at"]

                col1, col2, col3 = st.columns([3,1,3])

                with col1:
                    st.markdown(f"### {home}")

                with col2:
                    st.markdown("### vs")

                with col3:
                    st.markdown(f"### {away}")

                st.caption(time)

                st.divider()

###################################
# VALUE BET DETECTOR
###################################

with tab3:

    st.header("Value Bets")

    sample_odds = 2.40

    home_xg = home_attack[home_team] * away_defense[away_team] * league_home_goals
    away_xg = away_attack[away_team] * home_defense[home_team] * league_away_goals

    prob = home_xg / (home_xg + away_xg)

    implied = 1 / sample_odds

    value = prob - implied

    if value > 0.05:

        st.success("🔥 VALUE BET FOUND")

        st.write("Match:", home_team, "vs", away_team)

        st.write("Model probability:", round(prob*100,2), "%")

        st.write("Bookmaker odds:", sample_odds)

        st.write("Edge:", round(value*100,2), "%")

    else:

        st.info("No value bet detected")
