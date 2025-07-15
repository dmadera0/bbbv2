import sqlite3
import requests
import os
import json
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# API configuration
TEAMS_API_URL = "https://api.sportradar.com/mlb/trial/v8/en/league/teams.json"
API_KEY = os.getenv("SPORTRADAR_API_KEY")
if not API_KEY:
    raise ValueError("API key not found. Please set SPORTRADAR_API_KEY environment variable or create a .env file with SPORTRADAR_API_KEY.")

DB_PATH = os.path.abspath('baseball_analytics.db')
print(f"Using database: {DB_PATH}")

# Database setup
def setup_database():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Table 1: Teams
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS teams (
            id TEXT PRIMARY KEY,
            name TEXT,
            market TEXT,
            abbr TEXT
        )
    ''')
    
    conn.commit()
    conn.close()

# Populate teams
def populate_teams():
    url = TEAMS_API_URL + f"?api_key={API_KEY}"
    try:
        response = requests.get(url, timeout=10)
        print(f"Fetching teams, Status Code: {response.status_code}")
        response.raise_for_status()
        data = response.json()
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Track processed team IDs to avoid duplicates
        processed_team_ids = set()
        
        for team in data.get("teams", []):
            # Skip entries without market (e.g., leagues like "American League")
            if "market" in team:
                team_data = {
                    "id": team["id"],
                    "name": team["name"],
                    "market": team["market"],
                    "abbr": team["abbr"]
                }
                cursor.execute('''
                    INSERT OR REPLACE INTO teams (id, name, market, abbr)
                    VALUES (:id, :name, :market, :abbr)
                ''', team_data)
                processed_team_ids.add(team["id"])
            else:
                print(f"Skipping team {team['name']} (ID: {team['id']}) due to missing market")
        
        conn.commit()
        conn.close()
        print("Successfully imported teams")
    except requests.RequestException as e:
        print(f"API request failed for teams: {e}")
    except ValueError as e:
        print(f"JSON decode error for teams: {e}")
    except KeyError as e:
        print(f"KeyError for teams: {e}")

def main():
    setup_database()
    populate_teams()

if __name__ == "__main__":
    main()