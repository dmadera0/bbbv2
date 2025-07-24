# generate_team_stats.py (Selenium Version)
# Scrapes MLB team batting and pitching stats from https://www.mlb.com/stats/team using Selenium and saves to team_stats.csv

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import pandas as pd
import time
from sklearn.preprocessing import MinMaxScaler

# ----------------------
# Configure Selenium
# ----------------------
options = Options()
options.add_argument("--headless")  # run Chrome in background
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
driver = webdriver.Chrome(options=options)

# ----------------------
# Navigate to Batting Stats Page
# ----------------------
batting_url = "https://www.mlb.com/stats/team"
print(f"Loading page: {batting_url}")
driver.get(batting_url)
time.sleep(5)  # Wait for JavaScript to load table

# ----------------------
# Parse Batting Table
# ----------------------
print("Extracting batting table...")
table = driver.find_element(By.CSS_SELECTOR, "table")
rows = table.find_elements(By.CSS_SELECTOR, "tbody tr")

batting_columns = [
    "Team", "AVG", "OBP", "SLG", "OPS", "HR", "BB", "SO", "R", "AB", "H"
]
batting_data = []

for row in rows:
    cells = row.find_elements(By.TAG_NAME, "td")
    if len(cells) >= 11:
        team_data = [cell.text for cell in cells[:11]]
        batting_data.append(team_data)

batting_df = pd.DataFrame(batting_data, columns=batting_columns)

# ----------------------
# Navigate to Pitching Stats Page
# ----------------------
pitching_url = "https://www.mlb.com/stats/team/pitching"
