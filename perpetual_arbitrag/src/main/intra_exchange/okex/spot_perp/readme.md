## Perpetual - Spot arbitrag bot

### Example of execution
```python
python3 main/intra_exchange/okex/spot_perp/main.py \
--spot_trading_pair BTC-USDT \
--perpetual_trading_pair BTC-USDT-SWAP \
--api_key xxx \
--api_secret_key xxx \
--api_passphrase xxx \
--order_type market \
--spot_entry_vol 0.01 \
--max_spot_vol 0.1 \
--perpetual_entry_lot_size 10 \
--max_perpetual_lot_size 100 \
--entry_gap_frac 0 \
--profit_taking_frac -0.02 \
--poll_interval_s 1 \
--funding_interval_s 1800 \
--retry_timeout_s 30 \
--db_url xxx \
--fake_orders \
--funding_rate_disable
```

Flag / description pairs are explained below.

| Flag | Description | Example |
| --- | --- | --- |
| spot_trading_pair | Spot trading pair symbol on exchange | BTC-USDT |
| perpetual_trading_pair | Perpetual trading pair symbol on exchange |BTC-USDT-SWAP |
| api_key | Exchange API key for spot account | 0123456789asdzxc |
| api_secret_key | Exchange secret API key for perpetual account  | 0000-aaaa-123123-fsdfsd-123qwesad324 |
| api_passphrase | Exchange api passphrase for perpetual account | kucoinpassphrase |
| order_type | Either limit or market | limit or market |
| spot_entry_vol | Size of buy / sell for spot asset | 0.01 |
| max_spot_vol | Max Size of buy / sell for spot asset | 0.1 |
| perpetual_entry_lot_size | Lot size for buy / sell of perpetual asset | 10 |
| max_perpetual_lot_size | Max lot size for buy / sell of perpetual asset | 100 |
| futures_entry_leverage | Leverage for perpetual | 1 |
| entry_gap_frac | Ratio difference between spot / perpetual asset for consideration of entry | 0.001 |
| profit_taking_frac | Ratio difference for profit taking. For example, if we are short spot long perpetual, then if spot price goes above perpetual by the threshold, we immediately take profit | 0.0005 |
| poll_interval_s | Frequency (s) of polling API | 60 |
| fake_orders | If present, we execute fake trades. Remove if we want to place REAL trades | - |
| db_url | If present, trading bot state will be managed by the database under the URL specified. If None, we will revert to zero state execution (with no DB) | postgresql://user:pass@localhost:5432/schema |
| db_reset | If present, we will reset the state of the spot - trading pair in the DB. This means all will be set to 0 and written to the DB | - |
| funding_interval_s | Seconds before funding rate snapshot timing which we consider valid for taking into account estimated funding rate | 1800 |
| funding_rate_disable | If present, we do not take into account funding rate for trade decisions | - |
| retry_timeout_s | Wait seconds before retrying main loop | 30 |
