import streamlit as st
import requests
import pandas as pd

API_TOKEN = "5UyoUThTMPItCW81lTazLAgh3PM8QbHEjbXKBOcgBdrvBc4RSEvfhlGDUer6"

st.set_page_config(page_title="AI Football Predictor", layout="wide")

st.title("⚽ AI Football Predictor")

tab1, tab2, tab3 = st.tabs(["📅 Matches Today", "🧠 AI Prediction", "💰 Value Bets"])

# ---------------------------------------------------
# GET MATCHES
# ---------------------------------------------------

def get_matches():

    url = f"https://api.sportmonks.com/v3/football/fixtures/date/2026-03-26?api_token={API_TOKEN}&include=participants;league;predictions"

    r = requests.get(url)

    data = r.json()

    if "data" not in data:
        st.error("API Error")
        st.write(data)
        return []

    return data["data"]

matches = get_matches()

# ---------------------------------------------------
# MATCHES TODAY
# ---------------------------------------------------

with tab1:

    st.header("Today's Matches")

    leagues = {}

    for m in matches:

        league = m["league"]["name"]

        if league not in leagues:
            leagues[league] = []

        leagues[league].append(m)

    for league in leagues:

        st.subheader(league)

        for match in leagues[league]:

            home = match["participants"][0]["name"]
            away = match["participants"][1]["name"]

            logo_home = match["participants"][0]["image_path"]
            logo_away = match["participants"][1]["image_path"]

            time = match["starting_at"]

            col1,col2,col3 = st.columns([1,2,1])

            col1.image(logo_home,width=40)
            col2.write(f"**{home} vs {away}**")
            col3.image(logo_away,width=40)

            st.caption(time)

# ---------------------------------------------------
# AI PREDICTION
# ---------------------------------------------------

with tab2:

    st.header("AI Match Predictions")

    for match in matches:

        home = match["participants"][0]["name"]
        away = match["participants"][1]["name"]

        st.subheader(f"{home} vs {away}")

        predictions = match.get("predictions", [])

        for p in predictions:

            code = p["type"]["code"]

            if code == "fulltime-result-probability":

                home_p = p["predictions"]["home"]
                draw_p = p["predictions"]["draw"]
                away_p = p["predictions"]["away"]

                c1,c2,c3 = st.columns(3)

                c1.metric("Home Win",f"{home_p}%")
                c2.metric("Draw",f"{draw_p}%")
                c3.metric("Away Win",f"{away_p}%")

            if code == "over-under-2_5-probability":

                over = p["predictions"]["yes"]
                under = p["predictions"]["no"]

                st.write("Over 2.5:",over,"%")
                st.write("Under 2.5:",under,"%")

            if code == "both-teams-to-score-probability":

                yes = p["predictions"]["yes"]
                no = p["predictions"]["no"]

                st.write("BTTS Yes:",yes,"%")
                st.write("BTTS No:",no,"%")

        st.divider()

# ---------------------------------------------------
# VALUE BETS
# ---------------------------------------------------

with tab3:

    st.header("Value Bets Scanner")

    value_bets = []

    for match in matches:

        home = match["participants"][0]["name"]
        away = match["participants"][1]["name"]

        predictions = match.get("predictions", [])

        for p in predictions:

            if p["type"]["code"] == "fulltime-result-probability":

                home_prob = p["predictions"]["home"]

                if home_prob > 70:

                    value_bets.append({
                        "Match":f"{home} vs {away}",
                        "Pick":"Home Win",
                        "Probability":home_prob
                    })

    if len(value_bets) == 0:

        st.write("No strong value bets today")

    else:

        df = pd.DataFrame(value_bets)

        st.dataframe(df)
