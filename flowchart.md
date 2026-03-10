📥 DATA SOURCE
    Yahoo Finance API (yfinance)
         │
         ▼
⚙️ INGESTION (Phase 2)
    ingest_stocks.py
    • Fetches 2 years of OHLCV data
    • 8 tickers: AAPL, GOOGL, MSFT, JPM, SPY, TSLA, NVDA, QQQ
         │
         ▼
🗄️ RAW STORAGE
    DuckDB (stock_data.duckdb)
    └── raw_stock_prices table
         │
         ▼
🕐 ORCHESTRATION (Phase 3)
    Apache Airflow (via Astro CLI + Docker)
    └── stock_daily_ingestion DAG
        • Runs every weekday at 6pm
        • 8 tasks running sequentially
        • Auto-retries on failure
         │
         ▼
🔧 TRANSFORMATION (Phase 4 - next)
    dbt (stock_dbt project)
    ├── Staging Layer
    │   └── stg_stock_prices (clean columns, cast types)
    ├── Intermediate Layer
    │   └── int_daily_returns (daily % return per stock)
    └── Mart Layer
        └── fct_stock_metrics (moving averages, volatility)
         │
         ▼
📊 DASHBOARD (Phase 5)
    Streamlit or Looker Studio
    • Stock price over time
    • Daily returns comparison
    • 30-day volatility ranking