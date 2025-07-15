import sqlite3
import requests
import os
import json
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# API configuration
SCHEDULE_API_URL = "https://api.sportradar.com/mlb/trial/v8/en/games/2025/07/18/schedule.json"
TEAMS_API_URL = "https://api.sportradar.com/mlb/trial/v8/en/league/teams.json"
STATS_API_URL = "https://api.sportradar.com/mlb/trial/v8/en/seasons/2025/REG/teams/{team_id}/statistics.json"
API_KEY = os.getenv("SPORTRADAR_API_KEY")
if not API_KEY:
    raise ValueError("API key not found. Please set SPORTRADAR_API_KEY environment variable or create a .env file with SPORTRADAR_API_KEY.")

DB_PATH = os.path.abspath('baseball_analytics.db')
print(f"Using database: {DB_PATH}")

# Database setup
def setup_database():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Table 1: Schedule
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS schedule (
            game_id TEXT PRIMARY KEY,
            date TEXT,
            scheduled_time TEXT,
            home_team_id TEXT,
            away_team_id TEXT,
            venue_name TEXT,
            home_team_abbr TEXT,
            away_team_abbr TEXT,
            status TEXT,
            FOREIGN KEY (home_team_id) REFERENCES teams(id),
            FOREIGN KEY (away_team_id) REFERENCES teams(id)
        )
    ''')
    
    # Table 2: Teams
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS teams (
            id TEXT PRIMARY KEY,
            name TEXT,
            market TEXT,
            abbr TEXT
        )
    ''')
    
    # Table 3: Statistics
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS statistics (
            team_id TEXT PRIMARY KEY,
            season_id TEXT,
            year INTEGER,
            season_type TEXT,
            hitting_overall TEXT,  -- Store as JSON
            pitching_overall TEXT, -- Store as JSON
            fielding_overall TEXT, -- Store as JSON
            FOREIGN KEY (team_id) REFERENCES teams(id)
        )
    ''')
    
    conn.commit()
    conn.close()

# Populate schedule
def populate_schedule():
    url = SCHEDULE_API_URL + f"?api_key={API_KEY}"
    try:
        response = requests.get(url, timeout=10)
        print(f"Fetching schedule, Status Code: {response.status_code}")
        response.raise_for_status()
        data = response.json()
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        for game in data.get("games", []):
            game_data = {
                "game_id": game["id"],
                "date": data["date"],
                "scheduled_time": game["scheduled"],
                "home_team_id": game["home"]["id"],
                "away_team_id": game["away"]["id"],
                "venue_name": game["venue"]["name"],
                "home_team_abbr": game["home"]["abbr"],
                "away_team_abbr": game["away"]["abbr"],
                "status": game["status"]
            }
            cursor.execute('''
                INSERT OR REPLACE INTO schedule (game_id, date, scheduled_time, home_team_id, away_team_id, venue_name, home_team_abbr, away_team_abbr, status)
                VALUES (:game_id, :date, :scheduled_time, :home_team_id, :away_team_id, :venue_name, :home_team_abbr, :away_team_abbr, :status)
            ''', game_data)
        
        conn.commit()
        conn.close()
        print("Successfully imported schedule")
    except requests.RequestException as e:
        print(f"API request failed for schedule: {e}")
    except ValueError as e:
        print(f"JSON decode error for schedule: {e}")
    except KeyError as e:
        print(f"KeyError for schedule: {e}")

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
        
        for team in data.get("teams", []):
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
        
        conn.commit()
        conn.close()
        print("Successfully imported teams")
    except requests.RequestException as e:
        print(f"API request failed for teams: {e}")
    except ValueError as e:
        print(f"JSON decode error for teams: {e}")
    except KeyError as e:
        print(f"KeyError for teams: {e}")

# Populate statistics
def populate_statistics():
    # Fetch all team IDs to iterate over
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM teams")
    team_ids = [row[0] for row in cursor.fetchall()]
    conn.close()
    
    for team_id in team_ids:
        url = STATS_API_URL.format(team_id=team_id) + f"?api_key={API_KEY}"
        try:
            response = requests.get(url, timeout=10)
            print(f"Fetching stats for team {team_id}, Status Code: {response.status_code}")
            response.raise_for_status()
            data = response.json()
            
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            
            stats_data = {
                "team_id": team_id,
                "season_id": data["season"]["id"],
                "year": data["season"]["year"],
                "season_type": data["season"]["type"],
                "hitting_overall": json.dumps(data["statistics"]["hitting"]["overall"]),
                "pitching_overall": json.dumps(data["statistics"]["pitching"]["overall"]),
                "fielding_overall": json.dumps(data["statistics"]["fielding"]["overall"])
            }
            cursor.execute('''
                INSERT OR REPLACE INTO statistics (team_id, season_id, year, season_type, hitting_overall, pitching_overall, fielding_overall)
                VALUES (:team_id, :season_id, :year, :season_type, :hitting_overall, :pitching_overall, :fielding_overall)
            ''', stats_data)
            
            conn.commit()
            conn.close()
            print(f"Successfully imported stats for team {team_id}")
        except requests.RequestException as e:
            print(f"API request failed for team {team_id}: {e}")
        except ValueError as e:
            print(f"JSON decode error for team {team_id}: {e}")
        except KeyError as e:
            print(f"KeyError for team {team_id}: {e}")

def main():
    setup_database()
    populate_teams()
    populate_schedule()
    populate_statistics()

if __name__ == "__main__":
    main()