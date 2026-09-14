"""
Telegram notification service.
Loads credentials from .env and sends formatted messages to the user.
"""

import os
from pathlib import Path
import requests
from dotenv import load_dotenv

# Explicitly load backend/.env
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path, override=True)

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def escape_markdown_v2(text: str) -> str:
    """Escapes special characters required by Telegram's MarkdownV2 format."""
    if text is None:
        return "\\-"
    escape_chars = r'_*[]()~`>#+-=|{}.!'
    return ''.join(f'\\{char}' if char in escape_chars else char for char in str(text))

def send_telegram_alert(entry_dict: dict):
    """
    Sends a formatted alert to Telegram based on a TrackingEntry dict.
    
    Expected keys in entry_dict:
    ticker, signal, price, rsi, market_cap, pe_ratio, run_type
    """
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print(f"[Telegram] Missing credentials. Would have sent: {entry_dict.get('ticker')} {entry_dict.get('signal')}")
        return

    # Emojis for signals
    icon = "🟢" if entry_dict.get("signal") == "BUY" else "🔴"
    
    # Format the message
    ticker = escape_markdown_v2(entry_dict.get("ticker", "UNKNOWN"))
    signal = escape_markdown_v2(entry_dict.get("signal", ""))
    price = escape_markdown_v2(entry_dict.get("price", ""))
    rsi = escape_markdown_v2(entry_dict.get("rsi", ""))
    mcap = escape_markdown_v2(entry_dict.get("market_cap", "N/A"))
    pe = escape_markdown_v2(entry_dict.get("pe_ratio", "N/A"))
    run_type = escape_markdown_v2(entry_dict.get("run_type", "manual"))

    message = (
        f"{icon} *TAFA Alert: {ticker}*\n\n"
        f"*{signal}* Signal Triggered \\({run_type}\\)\n"
        f"• *Price:* ₹{price}\n"
        f"• *RSI:* {rsi}\n\n"
        f"*Fundamentals:*\n"
        f"• *Market Cap:* ₹{mcap} Cr\n"
        f"• *P/E Ratio:* {pe}"
    )

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "MarkdownV2",
        "disable_web_page_preview": True
    }
    
    try:
        response = requests.post(url, json=payload, timeout=5)
        response.raise_for_status()
        print(f"[Telegram] Successfully sent alert for {entry_dict.get('ticker')}")
    except Exception as e:
        print(f"[Telegram] Failed to send message: {e}")
