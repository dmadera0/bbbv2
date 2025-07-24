# generate_team_stats.py
# Fetches live MLB team stats and saves to team_stats.csv

import requests
import pandas as pd

# API endpoint for team stats
API_URL = "https://statsapi.mlb.com/api/v1/teams/stats"
params = {
    "leagueId": "103,104",  # American & National Leagues
    "season": "2024",       # Change to 2025 if season is ongoing
    "group": "hitting,pitching",
    "stats": "season"
}

response = requests.get(API_URL, params=params)
data = response.json()

teams = []
for team in data["stats"][0]["splits"]:
    team_name = team["team"]["name"]
    hitting = team["stat"]
    teams.append({
        "Team": team_name,
        "AVG": float(hitting.get("avg", 0)),
        "OBP": float(hitting.get("obp", 0)),
        "RunsPerGame": float(hitting.get("runsPerGame", 0))
    })

# Now fetch pitching stats from the second stat block
for team in data["stats"][1]["splits"]:
    team_name = team["team"]["name"]
    pitching = team["stat"]
    for row in teams:
        if row["Team"] == team_name:
            row["ERA"] = float(pitching.get("era", 0))
            row["WHIP"] = float(pitching.get("whip", 0))

# Save to CSV
df = pd.DataFrame(teams)
df = df.set_index("Team").sort_index()
df.to_csv("team_stats.csv")
print("✅ Saved team_stats.csv")