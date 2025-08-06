# train_model.py
import numpy as np
import pandas as pd
import joblib
import os
import json

MODELS_DIR = "models"
DATA_DIR = "data"

def load_model_and_predict(ticker: str, days_ahead: int, lookback: int = 5, model_type: str = 'linear'):
    """
    Loads a pre-trained model and uses pre-fetched local data to generate a forecast.
    This function makes NO external API calls.
    """
    model_filename = os.path.join(MODELS_DIR, f"{ticker}_{model_type}.joblib")
    data_filename = os.path.join(DATA_DIR, f"{ticker}.json")
    
    try:
        # Load the pre-trained model
        model = joblib.load(model_filename)
        
        # Load the local historical data
        with open(data_filename, 'r') as f:
            local_data = json.load(f)
        
        history = local_data.get('history', [])
        if len(history) < lookback:
            print(f"Not enough local history for {ticker}")
            return None

        # Get the last few days from our LOCAL data
        recent_closes = [item['close'] for item in history[-lookback:]]
        last_date_str = history[-1]['date']
        last_date = pd.to_datetime(last_date_str)
        
        predictions = []
        for i in range(1, days_ahead + 1):
            X_pred = np.array(recent_closes[-lookback:]).reshape(1, -1)
            next_close = model.predict(X_pred)[0]
            forecast_date = (last_date + pd.tseries.offsets.BDay(i)).strftime("%Y-%m-%d")
            predictions.append({"date": forecast_date, "close": float(next_close)})
            recent_closes.append(next_close)
            
        return predictions

    except FileNotFoundError:
        print(f"Model or data file not found for {ticker} ({model_type})")
        return None
    except Exception as e:
        print(f"An error occurred during prediction for {ticker}: {e}")
        return None