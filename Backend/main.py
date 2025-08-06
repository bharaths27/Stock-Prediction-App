# main.py
import json
import os
import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from train_model import load_model_and_predict

# --- Absolute Path Configuration ---
# Get the directory where this script (main.py) is located
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Build an absolute path to the 'data' directory
DATA_DIR = os.path.join(BASE_DIR, "data")

def get_sp500_companies():
    company_dict = {}
    try:
        if not os.path.exists(DATA_DIR):
            print(f"ERROR: Data directory not found at {DATA_DIR}")
            return {}
            
        for filename in os.listdir(DATA_DIR):
            if filename.endswith(".json"):
                file_path = os.path.join(DATA_DIR, filename)
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    company_dict[data['company_name']] = data['ticker']
    except Exception as e:
        print(f"Could not load companies from data files: {e}")
    return company_dict

COMPANY_NAME_TO_TICKER = get_sp500_companies()
print(f"✅ Loaded {len(COMPANY_NAME_TO_TICKER)} companies.")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/all_companies")
def get_all_companies():
    return list(COMPANY_NAME_TO_TICKER.keys())

@app.get("/stock/{input_str}")
def get_stock_data_from_file(input_str: str):
    query_lower = input_str.lower()
    match = next((name for name in COMPANY_NAME_TO_TICKER if query_lower in name.lower()), None)
    
    if not match:
        raise HTTPException(status_code=404, detail=f"No local data found for '{input_str}'.")
        
    ticker = COMPANY_NAME_TO_TICKER[match]
    file_path = os.path.join(DATA_DIR, f"{ticker}.json")

    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
        return data
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Data file for {ticker} not found.")

@app.get("/stock/history/{company_name}")
def get_stock_history_from_file(company_name: str, timeframe: str = "1Y"):
    ticker = COMPANY_NAME_TO_TICKER.get(company_name)
    if not ticker:
        raise HTTPException(status_code=404, detail="Company not found.")

    file_path = os.path.join(DATA_DIR, f"{ticker}.json")
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        history_df = pd.DataFrame(data['history'])
        history_df['date'] = pd.to_datetime(history_df['date'])
        end_date = history_df['date'].max()

        days_map = {"1D": 1, "1W": 7, "1M": 30, "6M": 182, "1Y": 365, "5Y": 1825}
        start_date = end_date - pd.Timedelta(days=days_map.get(timeframe, 365*100))
        
        filtered_history = history_df[history_df['date'] >= start_date]
        
        return {
            "company_name": company_name,
            "ticker": ticker,
            "history": filtered_history.to_dict('records')
        }
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Data file for {ticker} not found.")

@app.get("/stock/predict/{company_name}")
def predict_stock_price(company_name: str, timeframe: str = "1W", lookback: int = 5, model_type: str = 'linear'):
    if company_name not in COMPANY_NAME_TO_TICKER:
        raise HTTPException(status_code=404, detail="Company not found")

    ticker = COMPANY_NAME_TO_TICKER[company_name]
    days_ahead = {"1D": 1, "1W": 7, "1M": 30}.get(timeframe, 7)
    
    predictions = load_model_and_predict(ticker, days_ahead, lookback, model_type)

    if predictions is None:
        raise HTTPException(status_code=500, detail=f"Could not generate prediction. Pre-trained model for {ticker} ({model_type}) may be missing.")

    return {
        "company_name": company_name,
        "ticker": ticker,
        "timeframe": timeframe,
        "predictions": predictions
    }