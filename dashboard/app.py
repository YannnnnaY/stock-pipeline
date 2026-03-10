import streamlit as st
import duckdb
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

DB_PATH = "/Users/bliu/LearningProjects/stock-pipeline/stock_data.duckdb"

st.set_page_config(page_title="Stock Analytics Dashboard", layout="wide")
st.title("📈 Stock Market Analytics Pipeline")
st.markdown("Built with Python, Airflow, dbt, and DuckDB")

@st.cache_data
def load_data():
    conn = duckdb.connect(DB_PATH, read_only=True)
    df = conn.execute("SELECT * FROM fct_stock_metrics ORDER BY date").df()
    conn.close()
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
