from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import sys
sys.path.append("/Users/bliu/stock-pipeline")

from ingestion.ingest_stocks import fetch_stock_data, load_to_duckdb

TICKERS = ["AAPL", "GOOGL", "MSFT", "JPM", "SPY", "TSLA", "NVDA", "QQQ"]

default_args = {
    "owner": "airflow",
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

def ingest_ticker(ticker: str):
    df = fetch_stock_data(ticker)
    load_to_duckdb(df)

with DAG(
    dag_id="stock_daily_ingestion", # unique name for this pipeline
    default_args=default_args, #retries, delays set above
    description="Daily stock price ingestion", 
    schedule_interval="0 18 * * 1-5",  # runs weekdays at 6pm 
    start_date=datetime(2024, 1, 1), # when the DAG becomes active
    catchup=False, # don't run for past missed dates
) as dag:

    for ticker in TICKERS:
        PythonOperator(
            task_id=f"ingest_{ticker}",
            python_callable=ingest_ticker,
            op_kwargs={"ticker": ticker},
        )
