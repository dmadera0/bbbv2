import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from joblib import dump

# Create mock training data
np.random.seed(0)
df = pd.DataFrame({
    "home_offense": np.random.uniform(0.2, 0.8, 500),
    "away_offense": np.random.uniform(0.2, 0.8, 500),
    "home_pitching": np.random.uniform(0.2, 0.8, 500),
    "away_pitching": np.random.uniform(0.2, 0.8, 500),
    "home_win": np.random.choice([0, 1], size=500)
})

# Create feature matrix and labels
X = df[["home_offense", "away_offense", "home_pitching", "away_pitching"]]
y = df["home_win"]

# Train/test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

# Train model
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Save model
dump(model, "mlb_win_predictor.joblib")
print("✅ Model trained and saved as mlb_win_predictor.joblib")
