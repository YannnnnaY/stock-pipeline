import streamlit as st
import duckdb
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

DB_PATH = "/Users/bliu/LearningProjects/stock-pipeline/stock_data.duckdb"

st.set_page_config(page_title="Stock Analytics Dashboard", layout="wide")
st.title("Stock Market Analytics Pipeline")
st.markdown("Built with Python, Airflow, dbt, and DuckDB")

@st.cache_data
def load_data():
    # for local duckdb
    """conn = duckdb.connect(DB_PATH, read_only=True)
    df = conn.execute("SELECT * FROM fct_stock_metrics ORDER BY date").df()
    conn.close()"""
    # for streamlit app deploy
    df = pd.read_csv("data/exports/fct_stock_metrics.csv")
    return df

df = load_data()

# Sidebar filters
tickers = df["ticker"].unique().tolist()
selected_tickers = st.sidebar.multiselect("Select Tickers", tickers, default=tickers[:3])
df_filtered = df[df["ticker"].isin(selected_tickers)]

# Row 1: Stock prices
st.subheader("Stock Price Over Time")
fig1 = px.line(df_filtered, x="date", y="close", color="ticker")
st.plotly_chart(fig1, use_container_width=True)

# Row 2: Two columns
col1, col2 = st.columns(2)

with col1:
    st.subheader("30-Day Moving Average")
    fig2 = px.line(df_filtered, x="date", y="ma_30day", color="ticker")
    st.plotly_chart(fig2, use_container_width=True)

with col2:
    st.subheader("Daily Returns (%)")
    fig3 = px.line(df_filtered, x="date", y="daily_return_pct", color="ticker")
    st.plotly_chart(fig3, use_container_width=True)

# Row 3: Volatility
st.subheader("30-Day Volatility Ranking")
latest = df.groupby("ticker")["volatility_30day"].last().reset_index()
latest = latest.sort_values("volatility_30day", ascending=False)
fig4 = px.bar(latest, x="ticker", y="volatility_30day", color="ticker")
st.plotly_chart(fig4, use_container_width=True)


# Row 4: SPY Benchmark Comparison
st.subheader("Who Beat the Market? (vs SPY)")
st.markdown("Normalized to 100 at start date — shows cumulative return relative to SPY")

@st.cache_data
def load_benchmark():
    # for local duckdb
    '''conn = duckdb.connect(DB_PATH, read_only=True)
    df = conn.execute("""
        SELECT ticker, date, close
        FROM fct_stock_metrics
        ORDER BY ticker, date
    """).df()
    conn.close()'''
    # for streamlit app deploy
    df = pd.read_csv("data/exports/fct_stock_metrics.csv")
    return df

df_bench = load_benchmark()

# Normalize each ticker to 100 at its first date
df_bench["normalized"] = df_bench.groupby("ticker")["close"].transform(
    lambda x: x / x.iloc[0] * 100
)

# Get SPY as baseline
spy = df_bench[df_bench["ticker"] == "SPY"][["date", "normalized"]].rename(
    columns={"normalized": "SPY_baseline"}
)

# Merge SPY baseline into all tickers
df_bench = df_bench.merge(spy, on="date", how="left")
df_bench["vs_spy"] = df_bench["normalized"] - df_bench["SPY_baseline"]

# Plot normalized prices
fig5 = px.line(
    df_bench,
    x="date",
    y="normalized",
    color="ticker",
    title="Cumulative Return (Normalized to 100)"
)
fig5.add_hline(y=100, line_dash="dash", line_color="gray", annotation_text="Starting point")
st.plotly_chart(fig5, use_container_width=True)

# Plot outperformance vs SPY
st.subheader("Outperformance vs SPY")
latest_vs_spy = df_bench.groupby("ticker")["vs_spy"].last().reset_index()
latest_vs_spy = latest_vs_spy.sort_values("vs_spy", ascending=False)
latest_vs_spy["color"] = latest_vs_spy["vs_spy"].apply(
    lambda x: "outperformed" if x > 0 else "underperformed"
)
fig6 = px.bar(
    latest_vs_spy,
    x="ticker",
    y="vs_spy",
    color="color",
    color_discrete_map={"outperformed": "green", "underperformed": "red"},
    title="Total Return vs SPY (%)"
)
st.plotly_chart(fig6, use_container_width=True)



# row 5:Volatility Spikes Around Earnings
st.subheader("Volatility Spikes Around Earnings")
st.markdown("30-day rolling volatility for AAPL, GOOGL, TSLA with earnings dates marked")
# Known earnings dates for AAPL and GOOGL (last 2 years)
earnings_dates = {
    "AAPL": [
        "2024-02-01", "2024-05-02", "2024-08-01", "2024-10-31",
        "2025-01-30", "2025-05-01", "2025-07-31", "2025-10-30"
    ],
    "GOOGL": [
        "2024-01-30", "2024-04-25", "2024-07-23", "2024-10-29",
        "2025-02-04", "2025-04-29", "2025-07-29", "2025-10-28"
    ],
     "TSLA": [
        "2024-01-24", "2024-04-23", "2024-07-23", "2024-10-23",
        "2025-01-29", "2025-04-22", "2025-07-22", "2025-10-22"
    ]
}

df_earnings = df[df["ticker"].isin(["AAPL", "GOOGL", "TSLA"])].copy()

fig7 = px.line(
    df_earnings,
    x="date",
    y="volatility_30day",
    color="ticker",
    title="30-Day Volatility with Earnings Dates"
)

# Add vertical lines for earnings dates
colors = {"AAPL": "blue", "GOOGL": "red", "TSLA": "green"}
for ticker, dates in earnings_dates.items():
    for d in dates:
        fig7.add_vline(
            x=pd.Timestamp(d).timestamp() * 1000,
            line_dash="dot",
            line_color=colors[ticker],
            opacity=0.4,
            annotation_text=ticker,
            annotation_font_size=9
        )

st.plotly_chart(fig7, use_container_width=True)
