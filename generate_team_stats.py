# generate_team_stats.py (Selenium Version for Yahoo Sports)
# Scrapes MLB team batting and pitching stats from Yahoo Sports and saves to CSVs

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time

# ----------------------
# Configure Selenium Chrome Driver
# ----------------------
options = Options()
# options.add_argument("--headless")  # Temporarily disable headless mode for debugging
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

# Start the Chrome WebDriver with the configured options
driver = webdriver.Chrome(options=options)

# ----------------------
# Scrape Batting Stats from Yahoo Sports
# ----------------------
batting_url = "https://sports.yahoo.com/mlb/stats/team/?selectedTable=0&leagueStructure="
print(f"Loading batting stats page: {batting_url}")
driver.get(batting_url)

WebDriverWait(driver, 30).until(
    EC.presence_of_all_elements_located((By.CSS_SELECTOR, "table tbody tr"))
)
time.sleep(4)

print("Extracting batting table...")
table = driver.find_element(By.CSS_SELECTOR, "table")
rows = table.find_elements(By.CSS_SELECTOR, "tbody tr")

# Extract column headers from thead
thead = driver.find_element(By.CSS_SELECTOR, "table thead")
header_cells = thead.find_elements(By.TAG_NAME, "th")
batting_columns = [cell.text for cell in header_cells]

batting_data = []
for row in rows:
    cells = row.find_elements(By.TAG_NAME, "td")
    if len(cells) == len(batting_columns):
        team_data = [cell.text for cell in cells]
        batting_data.append(team_data)

batting_df = pd.DataFrame(batting_data, columns=batting_columns)
batting_df.to_csv("team_batting_stats.csv", index=False)
print("✅ team_batting_stats.csv saved with", len(batting_df), "teams")

# ----------------------
# Scrape Pitching Stats from Yahoo Sports
# ----------------------
pitching_url = "https://sports.yahoo.com/mlb/stats/team/?selectedTable=1&leagueStructure="
print(f"\nLoading pitching stats page: {pitching_url}")
driver.get(pitching_url)

WebDriverWait(driver, 30).until(
    EC.presence_of_all_elements_located((By.CSS_SELECTOR, "table tbody tr"))
)
time.sleep(4)

print("Extracting pitching table...")
table = driver.find_element(By.CSS_SELECTOR, "table")
rows = table.find_elements(By.CSS_SELECTOR, "tbody tr")

# Extract column headers from thead
thead = driver.find_element(By.CSS_SELECTOR, "table thead")
header_cells = thead.find_elements(By.TAG_NAME, "th")
pitching_columns = [cell.text for cell in header_cells]

pitching_data = []
for row in rows:
    cells = row.find_elements(By.TAG_NAME, "td")
    if len(cells) == len(pitching_columns):
        team_data = [cell.text for cell in cells]
        pitching_data.append(team_data)

pitching_df = pd.DataFrame(pitching_data, columns=pitching_columns)
pitching_df.to_csv("team_pitching_stats.csv", index=False)
print("✅ team_pitching_stats.csv saved with", len(pitching_df), "teams")

# ----------------------
# Cleanup
# ----------------------
driver.quit()
print("\n✅ Scraping complete. Batting and pitching stats saved from Yahoo Sports.")
