import requests
import pandas as pd

MAX_DATA_PER_REQUESTS 	= 200
EPOCH_START_TIME 		= 1630672572
EPOCH_END_TIME 			= 1638534972
INTERVAL_SEC 			= 60 * 60
SYMBOL 					= "XRPUSDTM"
SPOT_KLINES_BASE_URL 	= "https://api-futures.kucoin.com/api/v1/kline/query"
CSV_FILE 				= f"perpetual_prices_{EPOCH_START_TIME}_{EPOCH_END_TIME}_interval_{INTERVAL_SEC}.csv"

def interval_to_min(interval_sec):
	if interval_sec == 60:
		return 1
	elif interval_sec == 60 * 15:
		return 15
	elif interval_sec == 60 * 60:
		return 60

if __name__ == "__main__":
	time_interval_per_request = MAX_DATA_PER_REQUESTS * INTERVAL_SEC
	start_time 	= EPOCH_START_TIME
	end_time 	= start_time + time_interval_per_request
	price_data 	= []

	while start_time <= EPOCH_END_TIME:
		print(f"{start_time} - {end_time}")
		resp 		= requests.get(SPOT_KLINES_BASE_URL, params = 	{	"granularity" 	: interval_to_min(interval_sec = INTERVAL_SEC),
																		"symbol" 		: SYMBOL,
																		"from" 			: start_time * 1000,
																		"to" 			: end_time * 1000
																	})
		price_data 	+= resp.json()["data"]
		start_time 	= end_time
		end_time 	+= time_interval_per_request

	df 	= pd.DataFrame(price_data, columns = ["time", "open", "close", "high", "low", "volume"])
	df.to_csv(CSV_FILE)