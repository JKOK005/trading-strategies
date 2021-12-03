import requests
import pandas as pd

MAX_DATA_PER_REQUESTS 	= 1500
EPOCH_START_TIME 		= 1630644426
EPOCH_END_TIME 			= 1638506826
INTERVAL_SEC 			= 60
SYMBOL 					= "BTC-USDT"
SPOT_KLINES_BASE_URL 	= "https://api.kucoin.com/api/v1/market/candles"
CSV_FILE 				= f"spot_prices_{EPOCH_START_TIME}_{EPOCH_END_TIME}.csv"

def interval_to_str(interval_sec):
	if interval_sec == 60:
		return "1min"

if __name__ == "__main__":
	time_interval_per_request = MAX_DATA_PER_REQUESTS * INTERVAL_SEC
	start_time 	= EPOCH_START_TIME
	end_time 	= start_time + time_interval_per_request
	price_data 	= []

	while start_time <= EPOCH_END_TIME:
		print(f"{start_time} - {end_time}")
		resp 		= requests.get(SPOT_KLINES_BASE_URL, params = 	{	"type" 		: interval_to_str(interval_sec = INTERVAL_SEC),
																		"symbol" 	: SYMBOL,
																		"startAt" 	: start_time,
																		"endAt" 	: end_time
																	})
		price_data 	+= resp.json()["data"]
		start_time 	= end_time
		end_time 	+= time_interval_per_request

	df 	= pd.DataFrame(price_data, columns = ["time", "open", "close", "high", "low", "volume", "turnover"])
	df.to_csv(CSV_FILE)