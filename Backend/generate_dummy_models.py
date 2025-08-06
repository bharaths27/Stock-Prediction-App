# generate_dummy_models.py
import os
import joblib
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.tree import DecisionTreeRegressor

MODELS_DIR = "models"
DATA_DIR = "data"
os.makedirs(MODELS_DIR, exist_ok=True)

def generate_all_dummy_models():
    """
    Creates and saves blank, placeholder models for every stock in the data directory.
    This script runs offline and does not require any network access.
    """
    if not os.path.exists(DATA_DIR):
        print(f"Error: Data directory '{DATA_DIR}' not found.")
        return

    tickers = [f.split('.')[0] for f in os.listdir(DATA_DIR) if f.endswith(".json")]
    print(f"Found {len(tickers)} stocks. Generating dummy models...")

    # Create a tiny, generic dataset to make the models valid
    X_dummy = np.array([[100, 101, 102, 103, 104]])
    y_dummy = np.array([105])

    for ticker in tickers:
        try:
            # Create and "train" a dummy Linear Regression model
            linear_model = LinearRegression()
            linear_model.fit(X_dummy, y_dummy)

            # Create and "train" a dummy Decision Tree model
            tree_model = DecisionTreeRegressor()
            tree_model.fit(X_dummy, y_dummy)

            # Save both models to files
            joblib.dump(linear_model, os.path.join(MODELS_DIR, f"{ticker}_linear.joblib"))
            joblib.dump(tree_model, os.path.join(MODELS_DIR, f"{ticker}_tree.joblib"))

            print(f"-> Generated dummy models for {ticker}")

        except Exception as e:
            print(f"-> ❌ Failed to generate dummy models for {ticker}: {e}")

    print("\n✅ Dummy model generation complete.")

if __name__ == "__main__":
    generate_all_dummy_models()