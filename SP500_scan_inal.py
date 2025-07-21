import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

# Configuration
TICKERS_URL = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
SMA_SHORT = 20
SMA_LONG = 50
AROC_WEEKS = 20

# Fetch S&P 500 tickers
def get_sp500_tickers():
    try:
        tables = pd.read_html(TICKERS_URL)
        df = tables[0]
        return df["Symbol"].tolist()
    except Exception as e:
        print(f"Failed to fetch tickers: {e}")
        return []

# Fetch historical data (most recent 140 trading days)
def fetch_data(ticker):
    end_date = datetime.now()
    start_date = end_date - timedelta(weeks=30)
    try:
        df = yf.download(ticker, start=start_date, end=end_date, interval='1d', progress=False)

        # Flatten multi-index columns
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        return df
    except Exception as e:
        print(f"Error fetching data for {ticker}: {e}")
        return None

# Calculate technical indicators
def calc_indicators(df):
    try:
        df["SMA_short"] = df["Close"].rolling(window=SMA_SHORT).mean()
        df["SMA_long"] = df["Close"].rolling(window=SMA_LONG).mean()
        df["20w_high"] = df["Close"].rolling(window=100).max()  # Approx. 20 weeks of trading
        df["AROC"] = ((df["Close"] - df["Close"].shift(100)) / df["Close"].shift(100)) * 100
        return df
    except Exception as e:
        print(f"Indicator calculation error: {e}")
        return df

# Analyze one ticker
def analyze_ticker(ticker):
    df = fetch_data(ticker)
    if df is None or df.empty:
        return None

    print(f"{ticker} initial columns: {list(df.columns)}")

    df = calc_indicators(df)
    print(f"{ticker} after calc_indicators columns: {list(df.columns)}")

    latest = df.iloc[-1]

    try:
        if (
            latest["Close"] > latest["SMA_short"]
            and latest["SMA_short"] > latest["SMA_long"]
            and latest["Close"] >= 0.95 * latest["20w_high"]
            and latest["AROC"] > 5
        ):
            return {
                "Ticker": ticker,
                "Date": df.index[-1].strftime("%Y-%m-%d"),
                "Close": latest["Close"],
                "SMA_short": latest["SMA_short"],
                "SMA_long": latest["SMA_long"],
                "20w_high": latest["20w_high"],
                "AROC": latest["AROC"],
            }
    except Exception as e:
        print(f"⚠️ Error processing {ticker}: {e}")

    return None

# Main execution
def main():
    tickers = get_sp500_tickers()
    print(f"✅ Loaded {len(tickers)} tickers from S&P 500")

    results = []
    for ticker in tickers:
        result = analyze_ticker(ticker)
        if result:
            results.append(result)

    if results:
        df_results = pd.DataFrame(results)
        print("\n📈 Final Results:")
        print(df_results)
        df_results.to_csv("sp500_scan_output.csv", index=False)
    else:
        print("\n🚫 No tickers matched the criteria.")

if __name__ == "__main__":
    main()
