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

API_KEY = "wk_efa97ec4c9e3d71034ba1a48e73f3509"

url = f"https://api.the-odds-api.com/v4/sports/upcoming/odds/?apiKey={API_KEY}&regions=eu&markets=h2h"

response = requests.get(url)

games = response.json()

st.header("Today's Matches")

if isinstance(games, list):

    for game in games:

        home = game["home_team"]
        away = game["away_team"]

        st.write(home, "vs", away)

        bookmakers = game.get("bookmakers", [])

        if bookmakers:

            outcomes = bookmakers[0]["markets"][0]["outcomes"]

            home_odds = outcomes[0]["price"]
            away_odds = outcomes[1]["price"]

            st.write("Home odds:", home_odds)
            st.write("Away odds:", away_odds)

else:

    st.write("No matches today")
