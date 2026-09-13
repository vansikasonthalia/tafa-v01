# TAFA (Technical and Fundamental Analysis) V1

TAFA is a modern stock screener that allows you to upload a list of stocks, configure technical and fundamental rules, and automatically scan for buy/sell signals.

## Features

- **Custom Watchlists:** Upload CSV files of your favorite stocks to create a persistent universe.
- **Configurable Driver/Validation Logic:** 
  - **Driver:** Fast/Slow EMA crossover signals with AND/OR logic mapping.
  - **Validation:** RSI threshold and EMA(RSI) vs WMA(RSI) momentum indicators.
- **Fundamental Enhancements:** Automatically fetches and displays P/E ratio, Market Cap, Sales growth (3yr CAGR), Profit growth (3yr CAGR), and Market Cap to Sales ratio.
- **Auto-Screener:** Background scheduler runs the screener every 30 minutes on all your uploaded stocks.
- **Recommendations Log:** Keeps a historical track record of every BUY and SELL signal triggered by the engine.

## Technology Stack

- **Frontend:** Next.js, React, Vanilla CSS.
- **Backend:** FastAPI (Python), SQLAlchemy, SQLite.
- **Data Source:** Yahoo Finance (`yfinance` v1.7+ utilizing `curl_cffi` to bypass bot restrictions).

## Getting Started Locally

### 1. Backend Setup

Open a terminal in the `backend/` directory:

```bash
# Install dependencies
pip install -r requirements.txt

# Run the FastAPI server
python -m uvicorn main:app --reload --port 8000
```

### 2. Frontend Setup

Open a terminal in the `frontend/` directory:

```bash
# Install dependencies
npm install

# Run the development server
npm run dev
```

The application will be accessible at `http://localhost:3000`.

## Future Work / Roadmap

- Zerodha Kite Connect integration for real-time live market data.
- Fundamental Analysis filtering (currently displaying fundamental data on matched signals, but not actively filtering out matches based on it).
- Approvals flow for one-click trade execution.
