import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.abspath('baseball_analytics.db')

def get_db_connection():
    return sqlite3.connect(DB_PATH)

def show_all_teams():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name, market, abbr FROM teams ORDER BY market, name")
    teams = cursor.fetchall()
    conn.close()
    
    if teams:
        print("\nAll Teams:")
        for team in teams:
            print(f"{team[1]} {team[0]} ({team[2]})")
    else:
        print("\nNo teams found in the database.")

def get_team_stats(abbr):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT t.name, t.market, s.hitting_overall, s.pitching_overall, s.fielding_overall FROM teams t LEFT JOIN statistics s ON t.id = s.team_id WHERE t.abbr = ?", (abbr.upper(),))
    team_data = cursor.fetchone()
    conn.close()
    
    if team_data:
        name, market, hitting, pitching, fielding = team_data
        print(f"\nStats for {market} {name} ({abbr}):")
        print(f"Hitting Overall: {hitting}")
        print(f"Pitching Overall: {pitching}")
        print(f"Fielding Overall: {fielding}")
    else:
        print(f"\nNo stats found for team with abbreviation {abbr}.")

def get_todays_games():
    today = datetime.now().strftime("%Y-%m-%d")
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT game_id, scheduled_time, home_team_abbr, away_team_abbr, venue_name FROM schedule WHERE date = ?", (today,))
    games = cursor.fetchall()
    conn.close()
    
    if games:
        print(f"\nGames for {today}:")
        for game in games:
            print(f"Game ID: {game[0]}, Time: {game[1]}, {game[2]} vs {game[3]} at {game[4]}")
    else:
        print(f"\nNo games scheduled for {today}.")

def find_games_by_date():
    date = input("Enter date (YYYY-MM-DD): ")
    try:
        datetime.strptime(date, "%Y-%m-%d")
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT game_id, scheduled_time, home_team_abbr, away_team_abbr, venue_name FROM schedule WHERE date = ?", (date,))
        games = cursor.fetchall()
        conn.close()
        
        if games:
            print(f"\nGames for {date}:")
            for game in games:
                print(f"Game ID: {game[0]}, Time: {game[1]}, {game[2]} vs {game[3]} at {game[4]}")
        else:
            print(f"\nNo games scheduled for {date}.")
    except ValueError:
        print("\nInvalid date format. Please use YYYY-MM-DD.")

def main():
    while True:
        print("\nBaseball CLI Menu:")
        print("1. Show all teams")
        print("2. Team stats")
        print("3. Today's games")
        print("4. Find games")
        print("5. Exit")
        
        choice = input("Enter your choice (1-5): ")
        
        if choice == "1":
            show_all_teams()
        elif choice == "2":
            abbr = input("Enter team abbreviation (e.g., MIL): ")
            get_team_stats(abbr)
        elif choice == "3":
            get_todays_games()
        elif choice == "4":
            find_games_by_date()
        elif choice == "5":
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please enter a number between 1 and 5.")

if __name__ == "__main__":
    main()