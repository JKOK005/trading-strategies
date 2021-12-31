import numpy
import pandas as pd
import requests
import re
from datetime import datetime

class FetchGateKlinesPaginationData():

    API_ENDPOINT = "https://api.gateio.ws/api/v4/futures/usdt/candlesticks"

    def __init__(self, symbol, interval, start, end) -> None:
        self.symbol             = symbol
        self.interval           = interval
        self.start              = start
        self.end                = end
        self.current            = start
        self.points_per_query   = 500
        self.has_next           = True

    def __iter__(self):
        return self

    def interval_to_seconds(self):
        [_, number, time_str] = re.split(r'(\d+)', self.interval)
        number      = int(number)
        
        if time_str == "s":
            multiplier = 1
        elif time_str == "m":
            multiplier = 60
        elif time_str == "h":
            multiplier = 60 * 60
        return number * multiplier
            
    def __next__(self):
        interval_seconds    = self.interval_to_seconds() * self.points_per_query
        _start_time         = self.current
        _end_time           = self.current + interval_seconds

        if self.has_next is False:
            raise StopIteration()

        if  _end_time >= self.end:
            self.has_next   = False
            return self.fetch_next_page_data(start = _start_time, end = self.end)
        else:
            self.current    = _end_time
            return self.fetch_next_page_data(start = _start_time, end = _end_time -1)

    def fetch_next_page_data(self, start, end):
        query = {
            "contract"  : self.symbol,
            "from"      : start,
            "to"        : end,
            "interval"  : self.interval
        }

        resp = requests.get(self.API_ENDPOINT, params=query)
        print(self.API_ENDPOINT +'?'+'&'.join(['{}={}'.format(k,query[k]) for k in query.keys()]))
        klines = resp.json()
        return klines

def fetch_Gate_klines(symbol, start_time, end_time, interval):
    '''
    valid kline interval: [1m,3m,5m,15m,30m,1h,2h,4h,6h,8h,12h,1d,3d,1w,1M]
    '''
    start_time = datetime.fromisoformat(start_time)
    end_time = datetime.fromisoformat(end_time)

    started_timestamp = int(start_time.timestamp())
    ended_timestamp = int(end_time.timestamp())

    klines = []
    klines_fetcher = FetchGateKlinesPaginationData(symbol, interval, started_timestamp, ended_timestamp)

    for page_klines in klines_fetcher:
        klines += page_klines
    return klines

def download_klines_in_jupyter(symbol, start_time, end_time, interval):
    # start_time: YYYY-MM-DD
    # end_time: YYYY-MM-DD
    klines = fetch_Gate_klines(symbol, start_time, end_time, interval)

    default_output = f'Gate_kline_{symbol}{start_time}{end_time}_{interval}.csv'

    result = pd.DataFrame(klines).rename(columns = {
                                                    "t" : "OpeningTime", 
                                                    "o" : "Open",
                                                    "v" : "Volume",
                                                    "h" : "High",
                                                    "l" : "Low",
                                                    "c" : "Close"
                                                }
                                        )
    result['OpeningTime']   = numpy.vectorize(float)(result['OpeningTime'])
    result['OpeningTimeF']  = numpy.vectorize(datetime.fromtimestamp)(result['OpeningTime'])

    result.to_csv(default_output)
    print(f'saved to {default_output}')

if __name__ == "__main__":
    download_klines_in_jupyter('ETH_USDT', '2021-12-20', '2021-12-30', '5m')