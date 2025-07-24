# retrain_model.py
# This script retrains the MLB win prediction model using past predictions and outcomes

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from joblib import dump

# -------------------------------
# STEP 1: Load historical data
# -------------------------------
HISTORY_FILE = "mlb_prediction_history.csv"
MODEL_FILE = "mlb_win_predictor.joblib"

try:
    history_df = pd.read_csv(HISTORY_FILE)
except FileNotFoundError:
    print("❌ No history file found. Run predictions first to build history.")
    exit()

# Filter to only rows with known outcomes
history_df = history_df.dropna(subset=["Correct"])
if history_df.empty:
    print("❌ No completed games with outcomes available.")
    exit()

# -------------------------------
# STEP 2: Generate features and labels
# NOTE: Replace this with real stats later
# -------------------------------

np.random.seed(42)  # For reproducibility

# Generate mock features (replace with real team stats in the future)
X = pd.DataFrame({
    "home_offense": np.random.uniform(0.2, 0.8, len(history_df)),
    "away_offense": np.random.uniform(0.2, 0.8, len(history_df)),
    "home_pitching": np.random.uniform(0.2, 0.8, len(history_df)),
    "away_pitching": np.random.uniform(0.2, 0.8, len(history_df)),
})

# The target: 1 if our prediction was correct, 0 if not
# Alternatively, you could model the actual home win/loss directly using another column
y = history_df["Correct"].astype(int)

# -------------------------------
# STEP 3: Train the model
# -------------------------------
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Evaluate (optional print-out)
accuracy = model.score(X_test, y_test)
print(f"✅ Model retrained. Test Accuracy: {accuracy:.2%}")

# -------------------------------
# STEP 4: Save the model
# -------------------------------
dump(model, MODEL_FILE)
print(f"✅ Model saved to {MODEL_FILE}")
