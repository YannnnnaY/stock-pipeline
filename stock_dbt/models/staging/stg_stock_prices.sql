with source as (
    select * from raw_stock_prices
),

cleaned as (
    select
        ticker,
        cast(date as date) as date,
        round(open, 2) as open,
        round(high, 2) as high,
        round(low, 2) as low,
        round(close, 2) as close,
        volume
    from source
    where close is not null
      and volume > 0
)

select * from cleaned