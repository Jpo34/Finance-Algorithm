import yfinance as yf
import pandas as pd
import logging
from datetime import datetime, timedelta

# --- Configuration ---
TICKERS_URL = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
SMA_SHORT = 20
SMA_LONG = 50
AROC_WEEKS = 20
AROC_DAYS = AROC_WEEKS * 5  # Approx. trading days in 20 weeks

# --- Setup Logging ---
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

def get_sp500_tickers():
    """
    Fetch the list of S&P 500 tickers from Wikipedia.
    """
    try:
        tables = pd.read_html(TICKERS_URL)
        return tables[0]["Symbol"].tolist()
    except Exception as e:
        logging.error(f"Failed to fetch tickers: {e}")
        return []

def fetch_data(ticker):
    """
    Download recent historical data for a given ticker.
    """
    end_date = datetime.now()
    start_date = end_date - timedelta(weeks=30)

    try:
        df = yf.download(ticker, start=start_date, end=end_date, interval='1d', progress=False)
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        return df
    except Exception as e:
        logging.warning(f"Error fetching data for {ticker}: {e}")
        return None

def calc_indicators(df):
    """
    Calculate SMA, 20-week high, and Average Rate of Change.
    """
    try:
        df["SMA_short"] = df["Close"].rolling(window=SMA_SHORT).mean()
        df["SMA_long"] = df["Close"].rolling(window=SMA_LONG).mean()
        df["20w_high"] = df["Close"].rolling(window=AROC_DAYS).max()
        df["AROC"] = ((df["Close"] - df["Close"].shift(AROC_DAYS)) / df["Close"].shift(AROC_DAYS)) * 100
    except Exception as e:
        logging.error(f"Indicator calculation error: {e}")
    return df

def analyze_ticker(ticker):
    """
    Analyze a single ticker for technical signals.
    """
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
    except Exception as e:
        logging.warning(f"Error analyzing {ticker}: {e}")

    return None

def main():
    """
    Main entry point of the script.
    """
    tickers = get_sp500_tickers()
    logging.info(f"Loaded {len(tickers)} tickers.")

    results = []
    for ticker in tickers:
        result = analyze_ticker(ticker)
        if result:
            results.append(result)

    if results:
        df_results = pd.DataFrame(results)
        logging.info("\n📈 Final Results:")
        print(df_results)
        df_results.to_csv("sp500_scan_output.csv", index=False)
    else:
        logging.info("🚫 No tickers matched the criteria.")

if __name__ == "__main__":
    main()

