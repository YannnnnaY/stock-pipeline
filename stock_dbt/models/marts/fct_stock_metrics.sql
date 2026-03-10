with returns as (
    select * from {{ ref('int_daily_returns') }}
),

metrics as (
    select
        ticker,
        date,
        close,
        daily_return_pct,
        round(avg(close) over (
            partition by ticker 
            order by date 
            rows between 6 preceding and current row
        ), 2) as ma_7day,
        round(avg(close) over (
            partition by ticker 
            order by date 
            rows between 29 preceding and current row
        ), 2) as ma_30day,
        round(stddev(daily_return_pct) over (
            partition by ticker 
            order by date 
            rows between 29 preceding and current row
        ), 4) as volatility_30day
    from returns
)

select * from metrics