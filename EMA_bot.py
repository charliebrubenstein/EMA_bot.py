import yfinance as yf
import pandas as pd
import json
import os
import smtplib
from email.message import EmailMessage

# --- CONFIGURATION ---
MY_GMAIL = "Charliebrubenstien2009@gmail.com" 
GMAIL_APP_PASSWORD = os.environ.get('GMAIL_PASS')

TICKERS = [
    "NVDA", "AAPL", "MSFT", "GOOGL", "AVGO", "AMD", "TSM", "INTC", "META", "CRM",
    "ORCL", "ADBE", "CSCO", "TXN", "QCOM", "MU", "PLTR", "AMAT", "NOW", "ANET",
    "JPM", "V", "MA", "BAC", "GS", "MS", "AXP", "C", "WFC", "PYPL", "SCHW", "BLK",
    "SPGI", "CME", "COF", "AMP", "AFL", "COIN", "LLY", "UNH", "JNJ", "ABT", "MRK",
    "ABBV", "PFE", "AMGN", "GILD", "ISRG", "SYK", "VRTX", "AMZN", "WMT", "COST",
    "HD", "PG", "KO", "PEP", "MCD", "NKE", "SBUX", "TGT", "LOW", "TJX", "MELI",
    "XOM", "CVX", "CAT", "GE", "BA", "UPS", "UNP", "HON", "LMT", "DE", "FDX",
    "COP", "HAL", "SLB", "NEE", "VLO", "NFLX", "DIS", "VZ", "T", "TMUS", "UBER",
    "PLD", "AMT", "EQIX", "ABNB", "BKNG", "TSLA", "CMCSA", "PM", "WM", "ECL",
    "BTC-USD", "ETH-USD", "BMNR", "SI=F"
]

def send_me_email(subject, body):
    msg = EmailMessage()
    msg.set_content(body)
    msg['Subject'] = subject
    msg['From'] = MY_GMAIL
    msg['To'] = MY_GMAIL
    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(MY_GMAIL, GMAIL_APP_PASSWORD)
            smtp.send_message(msg)
    except Exception as e:
        print(f"Email failed: {e}")

def run_tracker():
    if os.path.exists('status.json'):
        with open('status.json', 'r') as f:
            prev_status = json.load(f)
    else:
        prev_status = {}

    current_status = {}
    print("Downloading market data...")
    data = yf.download(TICKERS, period="5d", interval="5m", group_by='ticker')

    for ticker in TICKERS:
        try:
            df = data[ticker].dropna()
            if len(df) < 200: continue
            
            ema50 = df['Close'].ewm(span=50, adjust=False).mean().iloc[-1]
            ema200 = df['Close'].ewm(span=200, adjust=False).mean().iloc[-1]
            
            new_state = "bullish" if ema50 > ema200 else "bearish"
            current_status[ticker] = new_state

            if ticker in prev_status:
                if prev_status[ticker] == "bearish" and new_state == "bullish":
                    send_me_email(f"BUY ALERT: {ticker}", f"{ticker} crossed Bullish (50 EMA > 200 EMA)")
                elif prev_status[ticker] == "bullish" and new_state == "bearish":
                    send_me_email(f"SELL ALERT: {ticker}", f"{ticker} crossed Bearish (50 EMA < 200 EMA)")
        except:
            continue

    with open('status.json', 'w') as f:
        json.dump(current_status, f)

if __name__ == "__main__":
    run_tracker()
