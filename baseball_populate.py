import sqlite3
import requests
import os
import json
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# API configuration
TEAMS_API_URL = "https://api.sportradar.com/mlb/trial/v8/en/league/teams.json"
STATS_API_URL = "https://api.sportradar.com/mlb/trial/v8/en/seasons/2025/REG/teams/{team_id}/statistics.json"
API_KEY = os.getenv("SPORTRADAR_API_KEY")
if not API_KEY:
    raise ValueError("API key not found. Please set SPORTRADAR_API_KEY environment variable or create a .env file with SPORTRADAR_API_KEY.")

DB_PATH = os.path.abspath('baseball_analytics.db')
print(f"Using database: {DB_PATH}")

# Database setup
def setup_database():
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        print("Creating teams table...")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS teams (
                id TEXT PRIMARY KEY,
                name TEXT,
                market TEXT,
                abbr TEXT
            )
        ''')
        
        print("Creating statistics table...")
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
        print("Database setup completed successfully")
    except sqlite3.Error as e:
        print(f"SQLite error during database setup: {e}")
    finally:
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
            if "market" in team and "abbr" in team:
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
                print(f"Skipping team {team['name']} (ID: {team['id']}) due to missing market or abbr")
        
        conn.commit()
        print("Successfully imported teams")
    except requests.RequestException as e:
        print(f"API request failed for teams: {e}")
    except ValueError as e:
        print(f"JSON decode error for teams: {e}")
    except KeyError as e:
        print(f"KeyError for teams: {e}")
    finally:
        conn.close()

# Populate statistics
def populate_statistics():
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
            print(f"Successfully imported stats for team {team_id}")
        except requests.RequestException as e:
            print(f"API request failed for team {team_id}: {e}")
        except ValueError as e:
            print(f"JSON decode error for team {team_id}: {e}")
        except KeyError as e:
            print(f"KeyError for team {team_id}: {e}")
        finally:
            conn.close()

def main():
    setup_database()
    populate_teams()
    populate_statistics()

if __name__ == "__main__":
    main()