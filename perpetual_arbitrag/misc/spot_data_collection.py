import requests
import pandas as pd
from time import sleep

MAX_DATA_PER_REQUESTS 	= 500
EPOCH_START_TIME 		= 1630672572
EPOCH_END_TIME 			= 1638534972
INTERVAL_SEC 			= 60
REQUEST_COOLDOWN_SEC 	= 10
SYMBOL 					= "XRP-USDT"
SPOT_KLINES_BASE_URL 	= "https://api.kucoin.com/api/v1/market/candles"
CSV_FILE 				= f"spot_prices_{EPOCH_START_TIME}_{EPOCH_END_TIME}_interval_{INTERVAL_SEC}.csv"

def interval_to_str(interval_sec):
	if interval_sec == 60:
		return "1min"
	elif interval_sec == 60 * 15:
		return "5min"
	elif interval_sec == 60 * 60:
		return "1hour"

if __name__ == "__main__":
	time_interval_per_request = MAX_DATA_PER_REQUESTS * INTERVAL_SEC
	start_time 	= EPOCH_START_TIME
	end_time 	= start_time + time_interval_per_request
	price_data 	= []

	while start_time <= EPOCH_END_TIME:
		try:
			print(f"{start_time} - {end_time}")
			resp 		= requests.get(SPOT_KLINES_BASE_URL, params = 	{	"type" 		: interval_to_str(interval_sec = INTERVAL_SEC),
																			"symbol" 	: SYMBOL,
																			"startAt" 	: start_time,
																			"endAt" 	: end_time
																		})
			price_data 	+= resp.json()["data"]
			start_time 	= end_time
			end_time 	+= time_interval_per_request
		except Exception as ex:
			print(resp.json())
			sleep(REQUEST_COOLDOWN_SEC)

	df 	= pd.DataFrame(price_data, columns = ["time", "open", "close", "high", "low", "volume", "turnover"])
	df.to_csv(CSV_FILE)