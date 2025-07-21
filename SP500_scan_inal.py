import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

# --- Config ---
TICKERS_URL = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
SMA_SHORT = 20
SMA_LONG = 50
AROC_WEEKS = 20
AROC_DAYS = AROC_WEEKS * 5  # 20 weeks ≈ 100 trading days

def get_sp500_tickers():
    try:
        tables = pd.read_html(TICKERS_URL)
        return tables[0]["Symbol"].tolist()
    except Exception as e:
        return []

def fetch_data(ticker):
    end_date = datetime.now()
    start_date = end_date - timedelta(weeks=30)

    try:
        df = yf.download(ticker, start=start_date, end=end_date, interval='1d', progress=False)
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        return df
    except Exception:
        return None

def calc_indicators(df):
    df["SMA_short"] = df["Close"].rolling(window=SMA_SHORT).mean()
    df["SMA_long"] = df["Close"].rolling(window=SMA_LONG).mean()
    df["20w_high"] = df["Close"].rolling(window=AROC_DAYS).max()
    df["AROC"] = ((df["Close"] - df["Close"].shift(AROC_DAYS)) / df["Close"].shift(AROC_DAYS)) * 100
    return df

def analyze_ticker(ticker):
    df = fetch_data(ticker)
    if df is None or df.empty:
        return None

    df = calc_indicators(df)

    try:
        latest = df.iloc[-1]
        if (
            latest["Close"] > latest["SMA_short"]
            and latest["SMA_short"] > latest["SMA_long"]
            and latest["Close"] >= 0.95 * latest["20w_high"]
            and latest["AROC"] > 5
        ):
            return {
                "Ticker": ticker,
                "Date": df.index[-1].strftime("%Y-%m-%d"),
                "Close": round(latest["Close"], 2),
                "SMA_short": round(latest["SMA_short"], 2),
                "SMA_long": round(latest["SMA_long"], 2),
                "20w_high": round(latest["20w_high"], 2),
                "AROC": round(latest["AROC"], 2),
            }
    except Exception:
        return None
    return None

def run_scan(limit=50):
    tickers = get_sp500_tickers()
    results = []

    for ticker in tickers[:limit]:  # Use limit to avoid Streamlit timeout
        result = analyze_ticker(ticker)
        if result:
            results.append(result)

    return pd.DataFrame(results)


