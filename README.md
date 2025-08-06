# Stock Prediction & Analysis Tool

![Stock Prediction App Screenshot](https://i.ibb.co/L5r64H0/image-00b703.jpg)

A full-stack application that provides historical stock data analysis and AI-powered price predictions using Linear Regression and Decision Tree models.

[**Live Demo**](#) &nbsp;&nbsp;&nbsp;
[**Portfolio Entry**](#) ---

## 💡 Key Features

* **Interactive Charting:** View historical stock performance across multiple timeframes (1D to Max).
* **Dual-Model AI Predictions:** Generate future price predictions using either a Linear Regression or a Decision Tree model.
* **Comprehensive Metrics:** Instantly access key financial metrics like Market Cap, P/E Ratio, and Dividend Yield.
* **Robust & Fast Architecture:** Built on a decoupled system that pre-caches data to ensure a fast, reliable user experience, overcoming the limitations of live public APIs.

---

## 🛠️ Tech Stack

* **Frontend:** React, Next.js, Tailwind CSS, Shadcn/UI, Recharts
* **Backend:** Python, FastAPI
* **Machine Learning:** Scikit-learn, Pandas
* **Deployment:** Vercel (Frontend), Render (Backend)

---

## 🏛️ Architectural Overview

This project uses a decoupled architecture to ensure high performance and reliability.

1.  **Offline Data Worker:** A Python script (`Backend/data_generator`) is used to pre-fetch and process data from the `yfinance` API. It stores the results in a local, file-based data store. This offline process isolates the main application from the unreliability and rate-limiting of the live API.
2.  **FastAPI Backend:** A lightweight Python server whose sole responsibility is to read from the pre-fetched data files and serve them to the frontend via a REST API. It also handles the on-the-fly training and prediction with the Scikit-learn models.
3.  **Next.js Frontend:** A modern, responsive user interface that consumes data from the FastAPI backend and provides interactive data visualizations.

---

## 🚀 Running Locally

1.  **Backend:**
    ```bash
    cd Backend
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    # The app uses pre-cached data in the /data folder.
    uvicorn main:app --reload
    ```
2.  **Frontend:**
    ```bash
    cd Frontend
    npm install
    npm run dev
    ```
