from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta

import sys
sys.path.append("/usr/local/airflow/include")

from ingest_stocks import fetch_stock_data, load_to_duckdb


TICKERS = ["AAPL", "NVDA", "GOOGL", "JPM", "SPY", "QQQ", "TSLA"]


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
    schedule="0 18 * * 1-5",  # runs weekdays at 6pm 
    start_date=datetime(2024, 1, 1), # when the DAG becomes active
    catchup=False, # don't run for past missed dates
) as dag:

    tasks = []
    for ticker in TICKERS:
        task = PythonOperator(
            task_id=f"ingest_{ticker}",
            python_callable=ingest_ticker,
            op_kwargs={"ticker": ticker},
        )
        tasks.append(task)

    # Chain tasks to run one after another
    for i in range(len(tasks) - 1):
        tasks[i] >> tasks[i + 1]
