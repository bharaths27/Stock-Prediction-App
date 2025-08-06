# generate_dummy_models.py
import os
import joblib
import numpy as np
import pandas as pd
import json
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor # Changed import

MODELS_DIR = "models"
DATA_DIR = "data"
os.makedirs(MODELS_DIR, exist_ok=True)

def generate_all_models_from_local_data():
    if not os.path.exists(DATA_DIR):
        print(f"Error: Data directory '{DATA_DIR}' not found.")
        return

    tickers = [f.split('.')[0] for f in os.listdir(DATA_DIR) if f.endswith(".json")]
    print(f"Found {len(tickers)} stocks. Generating models from local data...")

    for ticker in tickers:
        try:
            data_filename = os.path.join(DATA_DIR, f"{ticker}.json")
            with open(data_filename, 'r') as f:
                local_data = json.load(f)
            
            history = local_data.get('history', [])
            if len(history) < 10:
                print(f"-> Not enough local history for {ticker}. Skipping.")
                continue

            df = pd.DataFrame(history)
            lookback = 5
            for lag in range(1, lookback + 1):
                df[f"lag_{lag}"] = df["close"].shift(lag)
            df.dropna(inplace=True)

            feature_cols = [f"lag_{i}" for i in range(1, lookback + 1)]
            X_train = df[feature_cols].values
            y_train = df["close"].values

            linear_model = LinearRegression()
            linear_model.fit(X_train, y_train)
            
            # --- Changed from Decision Tree to Random Forest ---
            # n_estimators=50 means it will build 50 trees
            forest_model = RandomForestRegressor(n_estimators=50, random_state=42) 
            forest_model.fit(X_train, y_train)

            joblib.dump(linear_model, os.path.join(MODELS_DIR, f"{ticker}_linear.joblib"))
            # Save the new model with a new name
            joblib.dump(forest_model, os.path.join(MODELS_DIR, f"{ticker}_forest.joblib"))
            
            print(f"-> Generated models for {ticker}")
        
        except Exception as e:
            print(f"-> ❌ Failed to generate models for {ticker}: {e}")

    print("\n✅ Model generation complete.")

if __name__ == "__main__":
    generate_all_models_from_local_data()