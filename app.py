import streamlit as st
import pandas as pd
import numpy as np
from scipy.stats import poisson

st.title("⚽ Football Prediction Model")

data = pd.read_csv("E1.csv")

league_home_goals = data["FTHG"].mean()
league_away_goals = data["FTAG"].mean()

home_attack = data.groupby("HomeTeam")["FTHG"].mean() / league_home_goals
away_attack = data.groupby("AwayTeam")["FTAG"].mean() / league_away_goals

home_defense = data.groupby("HomeTeam")["FTAG"].mean() / league_away_goals
away_defense = data.groupby("AwayTeam")["FTHG"].mean() / league_home_goals

teams = sorted(list(home_attack.index))

home_team = st.selectbox("Home Team", teams)
away_team = st.selectbox("Away Team", teams)

if st.button("Predict"):

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

    st.subheader("Expected Goals")

    st.write(home_team, round(home_xg,2))
    st.write(away_team, round(away_xg,2))

    st.subheader("Match Probabilities")

    st.write("Home Win:", round(home_win*100,2), "%")
    st.write("Draw:", round(draw*100,2), "%")
    st.write("Away Win:", round(away_win*100,2), "%")
import requests
import streamlit as st

API_TOKEN = "5UyoUThTMPItCW81lTazLAgh3PM8QbHEjbXKBOcgBdrvBc4RSEvfhlGDUer6"

url = f"https://api.sportmonks.com/v3/football/fixtures/date/2026-03-26?api_token={API_TOKEN}&include=participants"

response = requests.get(url)

data = response.json()

st.header("Today's Matches")

for match in data["data"]:

    teams = match["participants"]

    home = teams[0]["name"]
    away = teams[1]["name"]

    time = match["starting_at"]

    st.write(home + " vs " + away + " | " + time)
