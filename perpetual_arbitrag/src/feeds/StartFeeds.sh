#!/bin/bash
<<com
Usage:

bash feeds/StartFeeds.sh \
-h <REDIS_HOST> \
-p <REDIS_PORT> \
-e <EXCHANGE> \
-c <CURRENCY PAIRS A> \
-c <CURRENCY PAIRS B> \
-c ...

Example:

bash feeds/StartFeeds.sh \
-h localhost \
-p 6379 \
-e OKX \
-c BTC-USDT,BTC-USDT-PERP \
-c DOT-USDT,DOT-USDT-PERP \
-c CFX-USDT,CFX-USDT-PERP
com

function cleanUpDocker {
	echo "Clean up containers"
	docker rm $(docker stop $(docker ps -a -q --filter label=cryptostore.exchange=$EXCHANGE))
	docker container prune -f
}

while getopts ":e::c::h::p:" opt; do
	case $opt in 
		e)
			EXCHANGE=$OPTARG
			;;
		c) 
			CURRENCY+=("$OPTARG")
			;;
		h)
			REDIS_HOST=$OPTARG
			;;
		p)
			REDIS_PORT=$OPTARG
			;;
		\?)
			echo "Invalid option: -$OPTARG"
			exit 1
			;;
		 :)
      		echo "Option -$OPTARG requires an argument"
      		exit 1
      		;;
	esac
done

trap cleanUpDocker EXIT

for CUR in "${CURRENCY[@]}"; do
	echo "$CUR on $EXCHANGE"

	docker run -d \
	--network=host \
	-e EXCHANGE=$EXCHANGE \
	-e CHANNELS='l2_book' \
	-e SYMBOLS=$CUR \
	-e BACKEND='REDIS' \
	-e HOST=$REDIS_HOST \
	-e PORT=$REDIS_PORT \
	-e SNAPSHOT_ONLY=True \
	-e SNAPSHOT_INTERVAL=1 \
	-l cryptostore.exchange=$EXCHANGE \
	ghcr.io/bmoscon/cryptostore:latest
done

while true; do
	for CUR in $(redis-cli -h $REDIS_HOST -p $REDIS_PORT --scan --pattern book-$EXCHANGE-*); do
		up_to_time=$(date --date='-10 seconds' '+%s')
		cmd="redis-cli -h $REDIS_HOST -p $REDIS_PORT ZREMRANGEBYSCORE $CUR 0 $up_to_time"
		echo $cmd
		eval $cmd
	done
	sleep 1
done