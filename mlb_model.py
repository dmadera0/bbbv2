# MLB Betting Prediction Model & Dashboard
# Streamlit App - MVP Version with MLB StatsAPI Scraper

import streamlit as st
import pandas as pd
import numpy as np
import requests
import os
import json
from datetime import date, datetime, timedelta

# -----------------------------
# CONFIG
# -----------------------------
CACHE_FILE = "mlb_games_cache.json"  # File to cache daily game data
MLB_API_SCHEDULE = "https://statsapi.mlb.com/api/v1/schedule"  # API endpoint for schedule info
MLB_API_TEAM_STATS = "https://statsapi.mlb.com/api/v1/teams/stats"  # Not used yet, but endpoint for stats
MLB_API_TEAMS = "https://statsapi.mlb.com/api/v1/teams"  # Not used yet, endpoint for team metadata

# -----------------------------
# DATA FETCHING & CACHING
# -----------------------------

def fetch_schedule(start_date, end_date):
    """Fetches MLB game schedule between given dates from MLB Stats API."""
    params = {
        "sportId": 1,  # MLB
        "startDate": start_date,
        "endDate": end_date,
        "hydrate": "probablePitcher,team,linescore"  # enriches the data with team and pitcher info
    }
    res = requests.get(MLB_API_SCHEDULE, params=params)
    res.raise_for_status()
    data = res.json()
    return data

def extract_game_data(schedule_json):
    """Extracts relevant game data (teams, pitchers, venue, date) from schedule JSON."""
    games = []
    for date_data in schedule_json.get("dates", []):
        for game in date_data.get("games", []):
            home = game["teams"]["home"]
            away = game["teams"]["away"]
            game_obj = {
                "Game": f"{away['team']['name']} @ {home['team']['name']}",
                "Home Team": home['team']['name'],
                "Away Team": away['team']['name'],
                "Date": game['gameDate'],
                "Venue": game.get('venue', {}).get('name', 'Unknown'),
                "Probable Home Pitcher": home.get("probablePitcher", {}).get("fullName", "TBD"),
                "Probable Away Pitcher": away.get("probablePitcher", {}).get("fullName", "TBD"),
                "GamePk": game["gamePk"]
            }
            games.append(game_obj)
    return pd.DataFrame(games)

def load_games_data():
    """Loads today's and tomorrow's games, using cache if available, otherwise fetches from API."""
    today = date.today()
    tomorrow = today + timedelta(days=1)

    # Check if cache file exists and is up to date
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, 'r') as f:
            cache = json.load(f)
        cache_date = cache.get("fetched_date")
        if cache_date == str(today):
            return pd.DataFrame(cache["games"])

    # Fetch new data and cache it
    schedule = fetch_schedule(today.isoformat(), tomorrow.isoformat())
    games_df = extract_game_data(schedule)
    with open(CACHE_FILE, 'w') as f:
        json.dump({
            "fetched_date": str(today),
            "games": games_df.to_dict(orient="records")
        }, f)
    return games_df

# -----------------------------
# MOCK MODEL OUTPUT (placeholder)
# -----------------------------
def add_mock_predictions(df):
    """
    Adds mock predictions for win probability, total runs, and margin for testing.
    
    TO DO: Replace this with your trained model predictions.
    Example:
    - Load a model with joblib
    - Generate features for each row
    - Run predictions and add output columns
    """
    df = df.copy()
    np.random.seed(42)
    df["Prob Home Win"] = np.random.uniform(0.4, 0.6, len(df))
    df["Total Runs"] = np.random.uniform(7.5, 10.5, len(df)).round(1)
    df["Margin"] = (df["Prob Home Win"] - 0.5) * 6  # range from -0.6 to +0.6 * 6 = -3.6 to +3.6
    df["Prediction"] = df.apply(lambda row: f"{row['Home Team'] if row['Prob Home Win'] >= 0.5 else row['Away Team']} Win", axis=1)
    return df

# Example inline steps to replace with real model:
# from joblib import load
# model = load("my_trained_model.joblib")
# X_features = generate_features(df)  # Write your own feature extraction logic
# df['Prob Home Win'] = model.predict_proba(X_features)[:, 1]
# df['Prediction'] = df['Prob Home Win'].apply(lambda p: 'Home Win' if p > 0.5 else 'Away Win')

# -----------------------------
# TEAM STATS EXTENSION (planned)
# -----------------------------
# To fetch team stats like win-loss record or batting averages, use MLB_API_TEAM_STATS
# def fetch_team_stats():
#     """Fetches season team stats for all MLB teams."""
#     res = requests.get(MLB_API_TEAM_STATS)
#     res.raise_for_status()
#     return res.json()  # You'll need to parse the JSON and join to game DataFrame

# -----------------------------
# UI HELPER
# -----------------------------
def get_game_insight(row):
    """Generates a text summary of the model's prediction for a specific game."""
    return f"**Prediction:** {row['Prediction']}\n\n" \
           f"**Confidence:** {'%.0f' % (row['Prob Home Win'] * 100 if 'Home' in row['Prediction'] else (1 - row['Prob Home Win']) * 100)}%\n\n" \
           f"**Expected Total Runs:** {row['Total Runs']}\n\n" \
           f"**Expected Margin:** {row['Margin']:.1f} runs\n\n" \
           f"Probable Pitchers: {row['Probable Away Pitcher']} (Away) vs {row['Probable Home Pitcher']} (Home)\n\n" \
           f"Venue: {row['Venue']}\n\n"

# -----------------------------
# STREAMLIT UI
# -----------------------------

# Set Streamlit page config and title
st.set_page_config(page_title="MLB Betting Model Dashboard", layout="wide")
st.title("MLB Game Predictions - AI Betting Model")

# Load and display game data with predictions
games_df = load_games_data()
games_df = add_mock_predictions(games_df)
st.subheader(f"Predictions for {date.today().strftime('%B %d, %Y')} and Tomorrow")

# Display each game's prediction with expandable detail
for idx, row in games_df.iterrows():
    with st.expander(f"{row['Game']} - {row['Prediction']}"):
        st.markdown(get_game_insight(row))

# Sidebar team filter
st.sidebar.header("Filter Options")
selected_team = st.sidebar.selectbox("Filter by Team", options=["All"] + sorted(set(games_df['Home Team']) | set(games_df['Away Team'])))

if selected_team != "All":
    filtered = games_df[(games_df['Home Team'] == selected_team) | (games_df['Away Team'] == selected_team)]
    st.subheader(f"Filtered Results for {selected_team}")
    for idx, row in filtered.iterrows():
        with st.expander(f"{row['Game']} - {row['Prediction']}"):
            st.markdown(get_game_insight(row))
