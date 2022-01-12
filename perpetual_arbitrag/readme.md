## Perpetual - Spot arbitrag bot

### Example of execution
```python
python3 main.py \
--spot_trading_pair BTC-USDT \
--futures_trading_pair XBTUSDTM \
--spot_api_key xxx \
--spot_api_secret_key xxx \
--spot_api_passphrase xxx \
--futures_api_key xxx \
--futures_api_secret_key xxx \
--futures_api_passphrase xxx \
--order_type market \
--spot_entry_vol 0.01 \
--max_spot_vol 0.1 \
--futures_entry_lot_size 10 \
--max_futures_lot_size 100 \
--futures_entry_leverage 1 \
--entry_gap_frac 0.01 \
--profit_taking_frac 0.005 \
--poll_interval_s 60 \
--funding_interval_s 1800 \
--retry_timeout_s 30 \
--db_url xxx \
--use_sandbox \
--fake_orders \
--funding_rate_disable
```

Flag / description pairs are explained below.

| Flag | Description | Example |
| --- | --- | --- |
| spot_trading_pair | Spot trading pair symbol on exchange | BTC-USDT |
| futures_trading_pair | Perpetual trading pair symbol on exchange |XBTUSDTM |
| spot_api_key | Exchange API key for spot account | 0123456789asdzxc |
| spot_api_secret_key | Exchange secret API key for spot account  | 0000-aaaa-123123-fsdfsd-123qwesad324 |
| spot_api_passphrase | Exchange api passphrase for spot account | kucoinpassphrase |
| futures_api_key | Exchange API key for perpetual account | 0123456789asdzxc |
| futures_api_secret_key | Exchange secret API key for perpetual account  | 0000-aaaa-123123-fsdfsd-123qwesad324 |
| futures_api_passphrase | Exchange api passphrase for perpetual account | kucoinpassphrase |
| order_type | Either limit or market | limit or market |
| spot_entry_vol | Size of buy / sell for spot asset | 0.01 |
| max_spot_vol | Max Size of buy / sell for spot asset | 0.1 |
| futures_entry_lot_size | Lot size for buy / sell of perpetual asset | 10 |
| max_futures_lot_size | Max lot size for buy / sell of perpetual asset | 100 |
| futures_entry_leverage | Leverage for perpetual | 1 |
| entry_gap_frac | Ratio difference between spot / perpetual asset for consideration of entry | 0.001 |
| profit_taking_frac | Ratio difference for profit taking. For example, if we are short spot long perpetual, then if spot price goes above perpetual by the threshold, we immediately take profit | 0.0005 |
| poll_interval_s | Frequency (s) of polling API | 60 |
| use_sandbox | If present, we use sandbox environment. Remove for REAL environment | - |
| fake_orders | If present, we execute fake trades. Remove if we want to place REAL trades | - |
| db_url | If present, trading bot state will be managed by the database under the URL specified. If None, we will revert to zero state execution (with no DB) | postgresql://user:pass@localhost:5432/schema |
| db_reset | If present, we will reset the state of the spot - trading pair in the DB. This means all will be set to 0 and written to the DB | - |
| funding_interval_s | Seconds before funding rate snapshot timing which we consider valid for taking into account estimated funding rate | 1800 |
| funding_rate_disable | If present, we do not take into account funding rate for trade decisions | - |
| retry_timeout_s | Wait seconds before retrying main loop | 30 |


### Transfer of main account funds to trade account
In order to ensure that trades are executed properly, we need 

1) Sufficient balance of the fiat currency in our trading account.

2) Sufficient balance of the fiat currency in our futures account.

3) API keys, API secret keys, Pass phrase for futures & spot account separately.


### Useful spot order apis
1) Creating a spot market order - `client.spot_trade.create_market_order(symbol = "BTC-USDT", side = "buy", price = 1, size = 10, type = "market")`

2) Creating a spot limit order - `client.spot_trade.create_market_order(symbol = "BTC-USDT", side = "buy", price = 1, size = 10, type = "limit")`
	- Limit orders are orders that are placed and awaiting fulfilment of the price condition
	- Market orders are orders that will be executed at the best available price. This is usually used for fast clearance of liquidity
	- Market orders are subjected to the price protection limit rule (https://land.kucoin.com/land/price-protect). The asset's price cannot go beyond a certain % value in order to protect the trader's interest

3) To cancel all orders - `client.spot_trade.cancel_all_orders()`

4) To get all orders placed - `client.spot_trade.get_order_list()`

5) To get all active orders placed - `client.spot_trade.get_order_list(status = "active")`
	- Active trades are placed under the "items"

6) To get all completed orders placed - `client.spot_trade.get_order_list(status = "done")`

7) To cancel specific order - `client.spot_trade.cancel_order(orderID)`


### Useful futures order apis
1) To get all active orders placed - `client.futures_trade.get_order_list(status = "active")`
	- Active trades are placed under the "items"

2) To get all positions currently being taken - `client.futures_trade.get_all_position()`
	- `isOpen` field indicates if the position is currently open
	- `currentQty` field indicates the lot size of the position taken
	- `avgEntryPrice` field indicates the average price entered into the position

3) To place an limit order - `client.futures_trade.create_limit_order(symbol = "XBTUSDM", type = "limit", side = "buy", lever = 1, size = 1, price = 58000)`

4) To find a currently active (unfulfilled) order - `client.futures_trade.get_order_list(status = "active")`

5) To cancel all limit orders - `client.futures_trade.cancel_all_limit_order(symbol = "XBTUSDM")`


### Bot flow chart
Overall execution flow of the program:
![bot-overview](img/spot-futures-arbitrag-bot-overview.png)

Trade execution logic:
![trade-logic](img/trading-execution.png)


### Unit test framework
Unit tests can be accessed using `pytest` framework. All tests are stored in the `tests` folder.

```python
pytest src/tests/*.py
```

### Init DB
If we want state management for the bot, we would have to connect the bot to some persistent storage, such as `PostgreSQL` or `MySQL`.

Use the script below to create the necessary schemas in the database.

```python
src/init_database.py
```


### Dockerizing application
Create a docker image for the arbitrag bot using

```bash
docker build -t arbitrag-bot:<version> -f ./Dockerfile .
```

Run `docker run` in order to create an executable container running the app

```bash
docker run \
--env SPOT_TRADING_PAIR=SAND-USDT \
--env FUTURES_TRADING_PAIR=SANDUSDTM \
--env SPOT_API_KEY=xxx \
--env SPOT_API_SECRET_KEY=xxx \
--env SPOT_API_PASSPHRASE=xxx \
--env FUTURES_API_KEY=xxx \
--env FUTURES_API_SECRET_KEY=xxx \
--env FUTURES_API_PASSPHRASE=xxx \
--env ORDER_TYPE=market \
--env SPOT_ENTRY_VOL=1 \
--env MAX_SPOT_VOL=3 \
--env FUTURES_ENTRY_LOT_SIZE=1 \
--env MAX_FUTURES_LOT_SIZE=3 \
--env FUTURES_ENTRY_LEVERAGE=1 \
--env ENTRY_GAP_FRAC=0.002 \
--env PROFIT_TAKING_FRAC=0.002 \
--env POLL_INTERVAL_S=10 \
--env FUNDING_INTERVAL_S=1800 \
--env DB_URL=xxx \
arbitrag-bot:<label>
```

*Note*: `db_reset` / `use_sandbox` / `fake_orders` / `funding_rate_disable` flags are not enabled when running in docker. These flags should not be used in production anyway.


### Miscellaneous
1) A short write up on how to determine the threshold for entry / take profit in lieu of trading fees can be found in [trading-threshold-eq](docs/trading-threshold-eq.pdf)
