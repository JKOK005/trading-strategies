FROM python:3.7.12
ENV workdir=/app
WORKDIR ${workdir}
COPY . ${workdir}
RUN pip3 --trusted-host=pypi.python.org --trusted-host=pypi.org --trusted-host=files.pythonhosted.org install -r requirements.txt

CMD [ "python", \
	  "./main.py", \
	  "--spot_trading_pair", "SXP-USDT", \
	  "--futures_trading_pair", "SXPUSDTM", \
	  "--spot_api_key", "xxx", \
	  "--spot_api_secret_key", "xxx", \
	  "--spot_api_passphrase", "xxx", \
	  "--futures_api_key", "xxx", \
	  "--futures_api_secret_key", "xxx", \
	  "--futures_api_passphrase", "xxx", \
	  "--order_type", "market", \
	  "--spot_entry_vol", "1", \
	  "--max_spot_vol", "3", \
	  "--futures_entry_lot_size", "1", \
	  "--max_futures_lot_size", "3", \
	  "--futures_entry_leverage", "1", \
	  "--entry_gap_frac", "0.002", \
	  "--profit_taking_frac", "0.002", \
	  "--poll_interval_s", "30", \
	  "--fake_orders" ]