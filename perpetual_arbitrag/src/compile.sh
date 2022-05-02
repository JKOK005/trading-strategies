#!/bin/bash
version='latest'

echo $version
echo "Compiling Kucoin bot"
docker build -t jkok005/kucoin-spot-perp-arb:$version -f ./main/intra_exchange/kucoin/spot_perp/Dockerfile .

echo "Compiling Okx bot"
docker build -t jkok005/okx-spot-perp-arb:$version -f ./main/intra_exchange/okx/spot_perp/Dockerfile .

echo "Compiling arbitrag bot manager"
docker build -t jkok005/arb-bot-manager:$version -f ./main/general/intra_exchange/Dockerfile .

echo "Compiling arbitrag bot scanner"
docker build -t jkok005/arb-bot-scanner:$version -f ./main/general/scanner/Dockerfile .

echo "Compiling Okx log listener"
docker build -t jkok005/okx-log-listener:$version -f ./main/general/listeners/Dockerfile .