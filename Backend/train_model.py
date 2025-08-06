import yfinance as yf
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.tree import DecisionTreeRegressor
from sklearn.metrics import r2_score

# In-memory dictionary to store trained models
models_dict = {}


def train_model_for_ticker(ticker: str, lookback: int = 5, model_type: str = 'linear'):
    """
    Trains a model (Linear Regression or Decision Tree) for a given ticker.
    """
    print(f"[TRAIN] Start training for {ticker} (lookback={lookback}, model={model_type})")
    stock = yf.Ticker(ticker)
    # Fetch a sufficient amount of data for training and feature creation
    hist = stock.history(period="2y")

    if hist.shape[0] < lookback + 20: # Ensure we have at least 20 samples to train on
        print(f"[TRAIN] Not enough data to train for {ticker}, skipping.")
        return

    # --- Feature Engineering ---
    df = hist[["Close"]].copy()
    df.reset_index(inplace=True)
    for lag in range(1, lookback + 1):
        df[f"lag_{lag}"] = df["Close"].shift(lag)
    df.dropna(inplace=True)

    if df.empty:
        print(f"[TRAIN] DataFrame is empty after feature engineering for {ticker}, skipping.")
        return

    feature_cols = [f"lag_{i}" for i in range(1, lookback + 1)]
    X_all = df[feature_cols].values
    y_all = df["Close"].values

    # Simple 80/20 train/test split
    split_index = int(len(X_all) * 0.8)
    X_train, X_test = X_all[:split_index], X_all[split_index:]
    y_train, y_test = y_all[:split_index], y_all[split_index:]

    # --- Model Selection ---
    if model_type == 'tree':
        # DecisionTreeRegressor for predicting continuous values
        # max_depth is a hyperparameter to prevent overfitting
        model = DecisionTreeRegressor(max_depth=5, random_state=42)
    else:
        # Default to Linear Regression
        model = LinearRegression()

    model.fit(X_train, y_train)

    # Evaluate on the test set
    y_pred = model.predict(X_test)
    r2 = r2_score(y_test, y_pred)
    print(f"[TRAIN] R2 score for {ticker} with {model_type} model: {r2:.4f}")

    # --- Store the trained model in the dictionary ---
    # We create a unique key for each model type and ticker
    model_key = f"{ticker}_{model_type}"
    models_dict[model_key] = {
        "model": model,
        "score": r2,
        "lookback": lookback
    }


def predict_future_closes(ticker: str, days_ahead: int, lookback: int = 5, model_type: str = 'linear'):
    """
    Iteratively predict multiple days into the future using the specified model type.
    """
    model_key = f"{ticker}_{model_type}"
    
    # Ensure we have a trained model; if not, train one.
    if model_key not in models_dict:
        train_model_for_ticker(ticker, lookback, model_type)
        # If training failed, the key will still not be in the dict
        if model_key not in models_dict:
            print(f"[PREDICT] Could not train model for {ticker}, returning empty list.")
            return []

    model_info = models_dict[model_key]
    model = model_info["model"]
    
    # --- Multi-step iterative prediction ---
    stock = yf.Ticker(ticker)
    # Fetch enough history to get the last 'lookback' days of valid closing prices
    hist = stock.history(period="1mo") 
    
    if hist.shape[0] < lookback:
        print(f"[PREDICT] Not enough recent data for multi-step forecast, returning empty list.")
        return []
    
    recent_closes = hist["Close"].values[-lookback:].tolist()
    predictions = []
    
    # Get the last valid date from the history to increment from
    last_date = hist.index[-1]
    
    for i in range(1, days_ahead + 1):
        # Prepare the feature vector for prediction
        X_pred = np.array(recent_closes[-lookback:]).reshape(1, -1)
        
        # Predict the next day's close
        next_close = model.predict(X_pred)[0]
        
        # Increment the date for the forecast
        # We use BDay (Business Day) to skip weekends in the forecast
        forecast_date = (last_date + pd.tseries.offsets.BDay(i)).strftime("%Y-%m-%d")
        
        predictions.append({
            "date": forecast_date,
            "close": float(next_close)
        })
        
        # Append the new prediction to the list of recent closes for the next iteration
        recent_closes.append(next_close)
        
    return predictions