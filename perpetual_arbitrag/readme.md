## Perpetual - Spot arbitrag bot

### Transfer of main account funds to trade account

In order to ensure that trades are executed properly, we need 

1) Sufficient balance of the fiat currency in our trading account.

2) 	


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

1) To get all active orders placed - `client.future_trade.get_order_list(status = "active")`
	- Active trades are placed under the "items"

2) To get all positions currently being taken - `client.futures_trade.get_all_position()`
	- `isOpen` field indicates if the position is currently open
	- `currentQty` field indicates the lot size of the position taken
	- `avgEntryPrice` field indicates the average price entered into the position

3) To place an order for a position ... 