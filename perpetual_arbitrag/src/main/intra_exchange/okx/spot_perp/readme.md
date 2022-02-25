## Perpetual - Spot arbitrag bot

### Example of execution
```python
python3 main/intra_exchange/okx/spot_perp/main.py \
--client_id 123asd \
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
--perpetual_leverage 1 \
--entry_gap_frac 0 \
--profit_taking_frac -0.02 \
--poll_interval_s 1 \
--current_funding_interval_s 1800 \
--estimated_funding_interval_s 1800 \
--funding_rate_disable 0 \
--retry_timeout_s 30 \
--db_url xxx \
--fake_orders \
--funding_rate_disable
```

Flag / description pairs are explained below.

| Flag | Description | Example |
| --- | --- | --- |
| client_id | Client ID registered on the exchange | 123asd |
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
| perpetual_leverage | Leverage size for perpetual trading | 1 |
| futures_entry_leverage | Leverage for perpetual | 1 |
| entry_gap_frac | Ratio difference between spot / perpetual asset for consideration of entry | 0.001 |
| profit_taking_frac | Ratio difference for profit taking. For example, if we are short spot long perpetual, then if spot price goes above perpetual by the threshold, we immediately take profit | 0.0005 |
| poll_interval_s | Frequency (s) of polling API | 60 |
| funding_rate_disable | If 1, we do not take into account funding rate for trade decisions. If 0, otherwise | 0 |
| fake_orders | If present, we execute fake trades. Remove if we want to place REAL trades | - |
| db_url | If present, trading bot state will be managed by the database under the URL specified. If None, we will revert to zero state execution (with no DB) | postgresql://user:pass@localhost:5432/schema |
| db_reset | If present, we will reset the state of the spot - trading pair in the DB. This means all will be set to 0 and written to the DB | - |
| current_funding_interval_s | Seconds before funding rate snapshot timing which we consider valid for taking into account current funding rate | 1800 |
| estimated_funding_interval_s | Seconds before funding rate snapshot timing which we consider valid for taking into account estimated funding rate | 1800 |
| retry_timeout_s | Wait seconds before retrying main loop | 30 |


### Minimum buffer size for spot trading
Fees in OKX are paid based on the spot currency traded. We have to ensure sufficient spot currencies in our account prior to trading, as these currencies will be used for paying the exchange fees for subsequent trades. 

The current solution is to ensure at least `1 lot` size of spot assets present before the trade is executed. In the case where the bot encounters the error `Insufficient spot buffer for trade ...`, simply ensure that the account has minimally 1 lot size of the asset and rerun the bot. 


### Executing docker image
Run `docker run` in order to create an executable container running the app

```bash
docker run \
--network=host \
--env CLIENT_ID=249746686270955520 \
--env SPOT_TRADING_PAIR=BTC-USDT \
--env PERPETUAL_TRADING_PAIR=BTC-USDT-SWAP \
--env API_KEY=27b1c671-xxx \
--env API_SECRET_KEY=xxx \
--env API_PASSPHRASE=xxx \
--env ORDER_TYPE=market \
--env SPOT_ENTRY_VOL=2 \
--env MAX_SPOT_VOL=10 \
--env PERPETUAL_ENTRY_LOT_SIZE=2 \
--env MAX_PERPETUAL_LOT_SIZE=10 \
--env PERPETUAL_LEVERAGE=1 \
--env ENTRY_GAP_FRAC=1 \
--env PROFIT_TAKING_FRAC=1 \
--env POLL_INTERVAL_S=1 \
--env CURRENT_FUNDING_INTERVAL_S=1800 \
--env ESTIMATED_FUNDING_INTERVAL_S=1800 \
--env FUNDING_RATE_DISABLE=0 \
--env RETRY_TIMEOUT_S=30 \
--env DB_URL=xxx \
<image>:<label>
```

*Note*: `db_reset` / `use_sandbox` / `fake_orders` / `funding_rate_disable` flags are not enabled when running in docker. These flags should not be used in production anyway.

In addition, consider adding `--network=host` for connecting the application to a local DB