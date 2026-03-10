# Stock Market Analytics Pipeline

An end-to-end data engineering and analytics project that ingests real-time stock market data, transforms it through a multi-layer data model, and serves insights via an interactive dashboard.

Built to demonstrate production-grade analytics engineering skills including pipeline orchestration, data modeling, testing, and visualization.

---

## Architecture

```
Yahoo Finance API
       │
       ▼
Python Ingestion Script (yfinance)
       │
       ▼
DuckDB Data Warehouse (raw_stock_prices)
       │
       ▼
Apache Airflow DAG (Astro CLI + Docker)
  • Runs every weekday at 6pm
  • 8 tickers ingested sequentially
  • Auto-retry on failure
       │
       ▼
dbt Transformation Layers
  ├── Staging:      stg_stock_prices       (cleaning, type casting)
  ├── Intermediate: int_daily_returns      (daily % return per stock)
  └── Mart:         fct_stock_metrics      (moving averages, volatility)
       │
       ▼
Streamlit Dashboard (Plotly charts)
```

---

## Tech Stack

| Layer | Tool |
|---|---|
| Ingestion | Python, yfinance, pandas |
| Storage | DuckDB |
| Orchestration | Apache Airflow, Astro CLI, Docker |
| Transformation | dbt (dbt-duckdb) |
| Testing & Docs | dbt tests, dbt docs |
| Visualization | Streamlit, Plotly |
| Version Control | Git, GitHub |

---

## Data Models

### Staging — `stg_stock_prices`
Cleans raw stock data: standardizes column names, casts types, filters null closes and zero-volume rows.

### Intermediate — `int_daily_returns`
Calculates daily percentage return per ticker using window functions (`LAG`).

### Mart — `fct_stock_metrics`
Final analytics-ready table with:
- 7-day moving average
- 30-day moving average
- 30-day rolling volatility (standard deviation of daily returns)

---

## Project Structure

```
stock-pipeline/
├── ingestion/
│   └── ingest_stocks.py       # Fetches stock data from Yahoo Finance
├── airflow/
│   ├── dags/
│   │   └── stock_ingestion_dag.py   # Airflow DAG for daily ingestion
│   ├── include/
│   │   └── ingest_stocks.py         # Ingestion script inside Docker
│   └── requirements.txt
├── stock_dbt/
│   ├── models/
│   │   ├── staging/
│   │   │   ├── stg_stock_prices.sql
│   │   │   └── schema.yml
│   │   ├── intermediate/
│   │   │   └── int_daily_returns.sql
│   │   └── marts/
│   │       └── fct_stock_metrics.sql
│   └── dbt_project.yml
├── dashboard/
│   └── app.py                 # Streamlit dashboard
└── README.md
```

---

## Getting Started

### Prerequisites
- Python 3.12
- Docker Desktop
- Astro CLI

### 1. Clone the repo
```bash
git clone https://github.com/YannnnnaY/stock-pipeline.git
cd stock-pipeline
```

### 2. Set up Python environment
```bash
python3.12 -m venv venv
source venv/bin/activate
pip install yfinance pandas duckdb dbt-duckdb streamlit plotly
```

### 3. Run initial ingestion
```bash
python3 ingestion/ingest_stocks.py
```

### 4. Run dbt transformations
```bash
cd stock_dbt
dbt run
dbt test
```

### 5. Start Airflow
```bash
cd airflow
astro dev start
```

### 6. Launch the dashboard
```bash
cd ..
streamlit run dashboard/app.py
```

---

## Dashboard Preview

> Stock price trends, daily returns, 30-day moving averages, and volatility ranking across 8 tickers: AAPL, GOOGL, MSFT, JPM, SPY, TSLA, NVDA, QQQ.

---

## 🧪 Data Quality Tests

dbt tests cover all key models:
- `not_null` checks on all critical columns
- Validated across staging, intermediate, and mart layers
- 8/8 tests passing

Run tests with:
```bash
cd stock_dbt
dbt test
```

---

## dbt Documentation

Auto-generated documentation including full lineage graph:
```bash
cd stock_dbt
dbt docs generate
dbt docs serve --port 8081
```

---

## Future Improvements
- Migrate from DuckDB to BigQuery or Snowflake for cloud scalability
- Add fundamental data (P/E ratio, earnings) from SEC EDGAR
- Implement data freshness tests in dbt
- Deploy Streamlit dashboard to Streamlit Cloud
- Add Slack alerting for Airflow task failures