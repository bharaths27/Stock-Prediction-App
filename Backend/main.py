# main.py
import json
import os
import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from train_model import predict_future_closes # Keep this for predictions

DATA_DIR = "data"

def get_sp500_companies():
    """Loads S&P 500 companies from the pre-fetched data files."""
    company_dict = {}
    try:
        # Reconstruct the list from the data files we have
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
    """Returns a list of all company names we have local data for."""
    return list(COMPANY_NAME_TO_TICKER.keys())

@app.get("/stock/{input_str}")
def get_stock_data_from_file(input_str: str):
    """
    Finds the best match and retrieves its pre-fetched data from a local file.
    """
    query_lower = input_str.lower()
    # Simple search: find the first key that contains the query
    match = next((name for name in COMPANY_NAME_TO_TICKER if query_lower in name.lower()), None)
    
    if not match:
        raise HTTPException(status_code=404, detail=f"No local data found for '{input_str}'. Try running the data fetcher.")
        
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
    """
    Reads historical data from a local file and filters by timeframe.
    """
    ticker = COMPANY_NAME_TO_TICKER.get(company_name)
    if not ticker:
        raise HTTPException(status_code=404, detail="Company not found.")

    file_path = os.path.join(DATA_DIR, f"{ticker}.json")
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)

        # Convert to DataFrame to easily filter by date
        history_df = pd.DataFrame(data['history'])
        history_df['date'] = pd.to_datetime(history_df['date'])
        end_date = history_df['date'].max()

        # Determine start date based on timeframe
        if timeframe == "1D": start_date = end_date - pd.Timedelta(days=1)
        elif timeframe == "1W": start_date = end_date - pd.Timedelta(days=7)
        elif timeframe == "1M": start_date = end_date - pd.Timedelta(days=30)
        elif timeframe == "6M": start_date = end_date - pd.Timedelta(days=182)
        elif timeframe == "1Y": start_date = end_date - pd.Timedelta(days=365)
        elif timeframe == "5Y": start_date = end_date - pd.Timedelta(days=365*5)
        else: start_date = history_df['date'].min()

        filtered_history = history_df[history_df['date'] >= start_date]
        
        return {
            "company_name": company_name,
            "ticker": ticker,
            "history": filtered_history.to_dict('records')
        }
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Data file for {ticker} not found.")

# The prediction endpoint remains unchanged as it has its own data logic
@app.get("/stock/predict/{company_name}")
def predict_stock_price(company_name: str, timeframe: str = "1W", lookback: int = 5, model_type: str = 'linear'):
    if company_name not in COMPANY_NAME_TO_TICKER:
        raise HTTPException(status_code=404, detail="Company not found")

    ticker = COMPANY_NAME_TO_TICKER[company_name]
    days_ahead = {"1D": 1, "1W": 7, "1M": 30}.get(timeframe, 7)
    predictions = predict_future_closes(ticker, days_ahead, lookback, model_type)

    if not predictions:
        raise HTTPException(status_code=500, detail="Could not generate prediction.")

    return {
        "company_name": company_name,
        "ticker": ticker,
        "timeframe": timeframe,
        "predictions": predictions
    }