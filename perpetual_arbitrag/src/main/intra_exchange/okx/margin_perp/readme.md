## Perpetual - Spot arbitrag bot

### Example of execution
```python
python3 main/intra_exchange/okx/margin_perp/main.py \
--client_id 123asd \
--margin_trading_pair BTC-USDT \
--perpetual_trading_pair BTC-USDT-SWAP \
--api_key xxx \
--api_secret_key xxx \
--api_passphrase xxx \
--order_type market \
--margin_entry_vol 0.01 \
--max_margin_vol 0.1 \
--margin_leverage 1 \
--margin_tax_rate 0.001 \
--margin_loan_period_hr 24 \
--perpetual_entry_lot_size 10 \
--max_perpetual_lot_size 100 \
--perpetual_leverage 1 \
--entry_gap_frac 0.01 \
--profit_taking_frac 0.005 \
--poll_interval_s 60 \
--current_funding_interval_s 1800 \
--estimated_funding_interval_s 1800 \
--funding_rate_disable 0 \
--retry_timeout_s 30 \
--db_url xxx \
--feed_url xxx \
--feed_port xxx \
--feed_latency_s 0.05
```

Flag / description pairs are explained below.

| Flag | Description | Example |
| --- | --- | --- |
| client_id | Client ID registered on the exchange | 123asd |
| margin_trading_pair | Margin trading pair symbol on exchange | BTC-USDT |
| perpetual_trading_pair | Perpetual trading pair symbol on exchange |BTC-USDT-SWAP |
| api_key | Exchange API key for spot account | 0123456789asdzxc |
| api_secret_key | Exchange secret API key for perpetual account  | 0000-aaaa-123123-fsdfsd-123qwesad324 |
| api_passphrase | Exchange api passphrase for perpetual account | kucoinpassphrase |
| order_type | Either limit or market | limit or market |
| margin_entry_vol | Size of buy / sell for margin asset | 0.01 |
| max_margin_vol | Max Size of buy / sell for margin asset | 0.1 |
| margin_leverage | Leverage size for margin trading | 1 |
| margin_tax_rate | Tax imposed by the exchange. Needed to offet margin entry / exit vol to maintain position balance | 0.001 |
| margin_loan_period_hr | How long do we expect to hold the position for? Needed to compute projected interest rate | 24 |
| perpetual_entry_lot_size | Lot size for buy / sell of perpetual asset | 10 |
| max_perpetual_lot_size | Max lot size for buy / sell of perpetual asset | 100 |
| perpetual_leverage | Leverage size for perpetual trading | 1 |
| entry_gap_frac | Ratio difference between spot / perpetual asset for consideration of entry | 0.001 |
| profit_taking_frac | Ratio difference for profit taking. For example, if we are short spot long perpetual, then if spot price goes above perpetual by the threshold, we immediately take profit | 0.0005 |
| poll_interval_s | Frequency (s) of polling API | 60 |
| current_funding_interval_s | Seconds before funding rate snapshot timing which we consider valid for taking into account current funding rate | 1800 |
| estimated_funding_interval_s | Seconds before funding rate snapshot timing which we consider valid for taking into account estimated funding rate | 1800 |
| funding_rate_disable | If 1, we do not take into account funding rate for trade decisions. If 0, otherwise | 0 |
| retry_timeout_s | Wait seconds before retrying main loop | 30 |
| db_url | If present, trading bot state will be managed by the database under the URL specified. If None, we will revert to zero state execution (with no DB) | postgresql://user:pass@localhost:5432/schema |
| feed_url | Price feed URL | - |
| feed_port | Price feed port | - |
| feed_latency_s | Permissible latency between retriving price feeds and computation in seconds | 0.08 |
| db_reset | If present, we will reset the state of the spot - trading pair in the DB. This means all will be set to 0 and written to the DB | - |

### Executing docker image
Run `docker run` in order to create an executable container running the app

```bash
docker run \
--network=host \
--env CLIENT_ID=249746686270955520 \
--env MARGIN_TRADING_PAIR=BTC-USDT \
--env PERPETUAL_TRADING_PAIR=BTC-USDT-SWAP \
--env ORDER_TYPE=market \
--env POLL_INTERVAL_S=0.1 \
--env MARGIN_ENTRY_VOL=2 \
--env MAX_MARGIN_VOL=10 \
--env MARGIN_LEVERAGE=1 \
--env MARGIN_TAX_RATE=0.001 \
--env MARGIN_LOAN_PERIOD_HR=24 \
--env PERPETUAL_ENTRY_LOT_SIZE=2 \
--env MAX_PERPETUAL_LOT_SIZE=10 \
--env PERPETUAL_LEVERAGE=1 \
--env ENTRY_GAP_FRAC=1 \
--env PROFIT_TAKING_FRAC=1 \
--env API_KEY=xxx \
--env API_SECRET_KEY=xxx \
--env API_PASSPHRASE=xxx \
--env CURRENT_FUNDING_INTERVAL_S=1800 \
--env ESTIMATED_FUNDING_INTERVAL_S=1800 \
--env RETRY_TIMEOUT_S=0.1 \
--env FUNDING_RATE_DISABLE=0 \
--env DB_URL=xxx \
--env FEEDS_URL=xxx \
--env FEEDS_PORT=xxx \
--env FEED_LATENCY_S=0.1 \
<image>:<label>
```

*Note*: `db_reset` / `use_sandbox` / `fake_orders` / `funding_rate_disable` flags are not enabled when running in docker. These flags should not be used in production anyway.

In addition, consider adding `--network=host` for connecting the application to a local DB