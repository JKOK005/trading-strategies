import argparse

if __name__ == "__main__":
	parser 	= argparse.ArgumentParser(description='Log listener')
	parser.add_argument('--client_id', type=str, nargs='?', default=os.environ.get("CLIENT_ID"), help='Client ID registered on the exchange')
	parser.add_argument('--api_key', type=str, nargs='?', default=os.environ.get("API_KEY"), help='Exchange api key')
	parser.add_argument('--api_secret_key', type=str, nargs='?', default=os.environ.get("API_SECRET_KEY"), help='Exchange secret api key')
	parser.add_argument('--api_passphrase', type=str, nargs='?', default=os.environ.get("API_PASSPHRASE"), help='Exchange api passphrase')
	parser.add_argument('--asset_pair', type=str, nargs='?', default=os.environ.get("ASSET_PAIR"), help='Asset pair traded')
	parser.add_argument('--whitelist_assets', type=str, nargs='+', default=os.environ.get("WHITELIST_ASSETS"), help='Only track logs pertaining to listed assets')
	args 	= parser.parse_args()