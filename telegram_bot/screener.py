import os
import time
import requests
import pandas as pd
import yfinance as yf
import pandas_ta as ta

# ==========================================
# CONFIGURATION
# ==========================================
# Read secrets from environment variables (GitHub Actions Secrets)
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# The universe of stocks to scan (Nifty 50 example, with .NS suffix for Yahoo Finance)
NIFTY_50 = [
    "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "ICICIBANK.NS", "BHARTIARTL.NS",
    "SBIN.NS", "INFY.NS", "LICI.NS", "ITC.NS", "HINDUNILVR.NS", "LT.NS",
    "BAJFINANCE.NS", "HCLTECH.NS", "MARUTI.NS", "SUNPHARMA.NS", "ONGC.NS",
    "KOTAKBANK.NS", "NTPC.NS", "TATAMOTORS.NS", "TITAN.NS", "ADANIENT.NS",
    "POWERGRID.NS", "ULTRACEMCO.NS", "COALINDIA.NS", "BAJAJFINSV.NS",
    "ASIANPAINT.NS", "M&M.NS", "ADANIPORTS.NS", "WIPRO.NS", "TATASTEEL.NS",
    "BAJAJ-AUTO.NS", "JSWSTEEL.NS", "NESTLEIND.NS", "GRASIM.NS", "HINDALCO.NS",
    "TECHM.NS", "CIPLA.NS", "INDUSINDBK.NS", "DRREDDY.NS", "EICHERMOT.NS",
    "APOLLOHOSP.NS", "TRENT.NS", "BRITANNIA.NS", "SHRIRAMFIN.NS", "HEROMOTOCO.NS",
    "HDFCLIFE.NS", "SBILIFE.NS", "BPCL.NS", "LTIM.NS", "DIVISLAB.NS"
]

# Configure strategy parameters
SMA_PERIOD = 50
RSI_PERIOD = 14
RSI_LOWER = 40
RSI_UPPER = 60
VOL_SMA_PERIOD = 20

# ==========================================
# TELEGRAM NOTIFIER
# ==========================================
def send_telegram_message(text: str):
    """Sends a markdown-formatted message to the Telegram chat."""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("Warning: Telegram credentials not found. Printing to console instead.")
        print(text)
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": "MarkdownV2",
        "disable_web_page_preview": True
    }
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        print("Telegram notification sent successfully.")
    except Exception as e:
        print(f"Failed to send Telegram message: {e}")

def escape_markdown_v2(text: str) -> str:
    """Escapes special characters required by Telegram's MarkdownV2 format."""
    escape_chars = r'_*[]()~`>#+-=|{}.!'
    return ''.join(f'\\{char}' if char in escape_chars else char for char in str(text))

# ==========================================
# DATA FETCHING & SCREENING
# ==========================================
def run_screener():
    print(f"Starting scan for {len(NIFTY_50)} stocks...")
    matches = []
    
    # To avoid rate limits and download efficiently, we use yf.download with group_by="ticker"
    # We fetch 3 months of data to ensure enough bars for a 50-day SMA
    try:
        # Download all data in one bulk request to prevent IP bans from sequential requests
        print("Fetching historical data (this may take a moment)...")
        data = yf.download(
            NIFTY_50, 
            period="3mo", 
            interval="1d", 
            group_by="ticker",
            threads=True,
            auto_adjust=True,
            progress=False
        )
    except Exception as e:
        send_telegram_message(f"🚨 *Screener Error*\nFailed to fetch data from Yahoo Finance: {escape_markdown_v2(str(e))}")
        return

    for ticker in NIFTY_50:
        try:
            # Extract single ticker DataFrame
            df = data[ticker] if len(NIFTY_50) > 1 else data
            
            # Drop NaN rows (e.g., if a stock didn't trade on a particular day)
            df = df.dropna(subset=['Close', 'Volume']).copy()
            
            if len(df) < SMA_PERIOD:
                print(f"Skipping {ticker}: Not enough data bars ({len(df)} < {SMA_PERIOD})")
                continue
                
            # Flatten multi-index columns if they exist (yfinance bulk download quirk)
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)

            # --- Calculate Indicators using pandas_ta ---
            df.ta.sma(length=SMA_PERIOD, append=True, col_names=(f"SMA_{SMA_PERIOD}",))
            df.ta.rsi(length=RSI_PERIOD, append=True, col_names=(f"RSI_{RSI_PERIOD}",))
            df.ta.sma(close=df['Volume'], length=VOL_SMA_PERIOD, append=True, col_names=(f"VOL_SMA_{VOL_SMA_PERIOD}",))
            
            # Get the latest completed daily candle
            latest = df.iloc[-1]
            
            if pd.isna(latest[f"SMA_{SMA_PERIOD}"]) or pd.isna(latest[f"RSI_{RSI_PERIOD}"]):
                continue
                
            current_close = float(latest["Close"])
            current_sma = float(latest[f"SMA_{SMA_PERIOD}"])
            current_rsi = float(latest[f"RSI_{RSI_PERIOD}"])
            current_vol = float(latest["Volume"])
            avg_vol = float(latest[f"VOL_SMA_{VOL_SMA_PERIOD}"])
            
            # --- Evaluate Strategy Rules ---
            cond_trend = current_close > current_sma
            cond_momentum = RSI_LOWER <= current_rsi <= RSI_UPPER
            cond_volume = current_vol > avg_vol
            
            if cond_trend and cond_momentum and cond_volume:
                # Stock matches all criteria!
                matches.append({
                    "Ticker": ticker.replace(".NS", ""),
                    "Close": round(current_close, 2),
                    "RSI": round(current_rsi, 1),
                    "Vol Spike": f"{round(current_vol / avg_vol, 1)}x"
                })
                
        except Exception as e:
            print(f"Error processing {ticker}: {e}")
            continue

    # ==========================================
    # BUILD AND SEND NOTIFICATION
    # ==========================================
    if not matches:
        send_telegram_message("📉 *Market Scan Complete*\nNo setups found today meeting the criteria\\.")
        return
        
    # Build markdown table
    message = "📈 *Stock Screener Matches*\n\n"
    message += "```\n" # Monospace block for alignment
    message += f"{'TICKER':<12} | {'PRICE':<8} | {'RSI':<5} | {'VOL'}\n"
    message += "-" * 38 + "\n"
    
    for m in matches:
        message += f"{m['Ticker']:<12} | {m['Close']:<8.2f} | {m['RSI']:<5.1f} | {m['Vol Spike']}\n"
        
    message += "```\n"
    message += f"_{len(matches)} stocks in pullback/consolidation zone\\._"
    
    send_telegram_message(message)

if __name__ == "__main__":
    run_screener()
