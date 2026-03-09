import yfinance as yf
import duckdb
import pandas as pd

# stocks to track
TICKERS = ['AAPL', 'NVDA', 'GOOGL', 'JPM', 'SPY', 'QQQ', 'TSLA']


def fetch_stock_data(ticker: str) -> pd.DataFrame:
    stock = yf.Ticker(ticker)
    df = stock.history(period="2y")
    df = df.reset_index()
    df["ticker"] = ticker
    df = df[["ticker", "Date", "Open", "High", "Low", "Close", "Volume"]]
    df.columns = ["ticker", "date", "open", "high", "low", "close", "volume"]
    return df


def load_to_duckdb(df: pd.DataFrame, db_path: str = "stock_data.duckdb"):
    conn = duckdb.connect(db_path)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS raw_stock_prices (
            ticker VARCHAR,
            date TIMESTAMP,
            open DOUBLE,
            high DOUBLE,
            low DOUBLE,
            close DOUBLE,
            volume BIGINT
        )
    """)
    conn.execute("INSERT INTO raw_stock_prices SELECT * FROM df")
    conn.close()
    print(f"Loaded {len(df)} rows for {df['ticker'].iloc[0]}")



if __name__ == "__main__":
    for ticker in TICKERS:
        print(f"Fetching {ticker}...")
        df = fetch_stock_data(ticker)
        load_to_duckdb(df)
    print("All done!")
