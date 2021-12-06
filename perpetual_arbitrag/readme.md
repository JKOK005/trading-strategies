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
--futures_entry_lot_size 10 \
--futures_entry_leverage 1 \
--entry_gap_frac 0.1 \
--poll_interval_s 60 \
--use_sandbox
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
| futures_entry_lot_size | Lot size for buy / sell of perpetual asset | 10 |
| futures_entry_leverage | Leverage for perpetual | 1 |
| entry_gap_frac | Ratio difference between spot / perpetual asset for consideration of entry | 0.001 |
| poll_interval_s | Frequency (s) of polling API | 60 |
| use_sandbox | If present, we use sandbox environment. Remove for REAL environment | - |


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
