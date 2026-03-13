import streamlit as st
import pandas as pd
import numpy as np
from scipy.stats import poisson
import requests

st.set_page_config(page_title="AI Football Predictor", layout="wide")

st.title("⚽ AI Football Predictor")

#############################
# LOAD MULTIPLE LEAGUES
#############################

files = [
    "E0 (2).csv",   # Premier League
    "E1.csv",       # Championship
    "SP1.csv",      # La Liga
    "I1.csv",       # Serie A
    "D1.csv",       # Bundesliga
    "G1.csv"        # Greece
]

dfs = []

for f in files:
    try:
        df = pd.read_csv(f)
        dfs.append(df)
    except:
        pass

data = pd.concat(dfs)

#############################
# MODEL CALCULATION
#############################

league_home_goals = data["FTHG"].mean()
league_away_goals = data["FTAG"].mean()

home_attack = data.groupby("HomeTeam")["FTHG"].mean() / league_home_goals
away_attack = data.groupby("AwayTeam")["FTAG"].mean() / league_away_goals

home_defense = data.groupby("HomeTeam")["FTAG"].mean() / league_away_goals
away_defense = data.groupby("AwayTeam")["FTHG"].mean() / league_home_goals

teams = sorted(list(home_attack.index))

st.sidebar.header("Match Prediction")

home_team = st.sidebar.selectbox("Home Team", teams)
away_team = st.sidebar.selectbox("Away Team", teams)

#############################
# PREDICTION
#############################

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

    st.write("Expected Goals")
    st.write(home_team, round(home_xg,2))
    st.write(away_team, round(away_xg,2))

#############################
# TODAY MATCHES (API)
#############################

st.header("Today's Matches")

API_TOKEN = "ΒΑΛΕ_TOKEN"

url = f"https://api.sportmonks.com/v3/football/fixtures/date/2026-03-26?api_token={API_TOKEN}&include=participants"

response = requests.get(url)

matches = response.json()["data"]

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
