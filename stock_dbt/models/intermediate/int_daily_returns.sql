with staging as (
    select * from {{ ref('stg_stock_prices') }}
),

returns as (
    select
        ticker,
        date,
        close,
        lag(close) over (partition by ticker order by date) as prev_close,
        round(
            (close - lag(close) over (partition by ticker order by date)) 
            / lag(close) over (partition by ticker order by date) * 100
        , 4) as daily_return_pct
    from staging
)

select * from returns
where prev_close is not null